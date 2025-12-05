import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from fastapi import HTTPException, status
from threading import RLock  # NEW

from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut

try:  # Prefer legacy module path used by tests if available
    from repositories.movie_repo import MovieRepository, ReviewRepository  # type: ignore
except ModuleNotFoundError:  # Fallback to the canonical backend package when running the app
    from backend.repositories.movie_repo import MovieRepository, ReviewRepository


# NEW: lock to protect read-modify-write review+metadata sequences
_REVIEW_RMW_LOCK = RLock()

class ReviewService:
    """
    Provide high-level operations for creating, updating, and deleting movie reviews.
    """

    def _parse_datetime(self, value):
        """
        Accept a variety of date formats:
        - ISO strings (with or without Z)
        - \"25 May 2005\" / \"14 Feb 2005\" style
        - Fallback to epoch if unparseable
        """
        if value is None:
            return datetime.fromtimestamp(0, tz=timezone.utc)
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

        text = str(value).strip()
        # handle trailing Z
        if text.endswith("Z"):
            text = text[:-1]

        # Try ISO first
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(text, fmt)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except Exception:
                continue

        # Try long/short month names
        for fmt in ("%d %B %Y", "%d %b %Y"):
            try:
                parsed = datetime.strptime(text, fmt)
                return parsed.replace(tzinfo=timezone.utc)
            except Exception:
                continue

        return datetime.fromtimestamp(0, tz=timezone.utc)

    def _prepare_review_out(self, user_id: str, record: dict, id_to_name: Optional[Dict[str, str]] = None) -> ReviewOut:
        """
        Build a ReviewOut with parsed datetimes and coerced numeric fields.
        """
        created_raw = record.get("created_at") or record.get("timestamp") or record.get("updated_at")
        updated_raw = record.get("updated_at") or record.get("timestamp") or record.get("created_at")
        return ReviewOut(
            user_id=user_id,
            username=record.get("username") or (id_to_name or {}).get(user_id),
            rating=float(record.get("rating") or 0.0),
            review_text=record.get("review_text"),
            upvotes=int(record.get("upvotes") or 0),
            downvotes=int(record.get("downvotes") or 0),
            created_at=self._parse_datetime(created_raw),
            updated_at=self._parse_datetime(updated_raw),
        )

    def _load_usernames(self) -> Dict[str, str]:
        """
        Load a map of user_id -> username from users.json. Returns {} if missing.
        """
        users_file = Path(__file__).resolve().parents[1] / "data" / "users.json"
        if not users_file.exists():
            return {}
        try:
            with users_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return {}
        id_to_name: Dict[str, str] = {}
        if isinstance(data, list):
            for u in data:
                uid = u.get("id")
                uname = u.get("username")
                if uid and uname:
                    id_to_name[uid] = uname
        elif isinstance(data, dict):
            # support alternative shape if ever used
            for u in data.get("users", []):
                uid = u.get("id")
                uname = u.get("username")
                if uid and uname:
                    id_to_name[uid] = uname
        return id_to_name

    def list_reviews(self, movie_id: str, sort: str = "recent"):
        """
        Return list of reviews for a movie sorted by 'upvotes' or 'recent'.
        """
        id_to_name = self._load_usernames()
        data = ReviewRepository.get_review_data(movie_id)
        reviews_map = data.get("reviews", {})
        items = []
        for user_id, r in reviews_map.items():
            items.append(self._prepare_review_out(user_id, r, id_to_name))

        if sort == "upvotes":
            items.sort(key=lambda x: (x.upvotes, x.created_at), reverse=True)
        else:
            # default to recent
            items.sort(key=lambda x: x.created_at, reverse=True)
        return items

    def _ensure_movie_exists(self, movie_id: str) -> None:
        """
        Raise HTTP 404 if the movie does not exist in the repository.
        """
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="movie not found")

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        """
        Create or update a user's review for a movie and keep aggregated rating metadata in sync.
        """
        with _REVIEW_RMW_LOCK:
            self._ensure_movie_exists(movie_id)
            metadata = MovieRepository.get_movie_metadata(movie_id)
            review_data = ReviewRepository.get_review_data(movie_id)

            current = review_data["reviews"].get(user_id)
            now = datetime.now(timezone.utc)

            if current:
                old_rating = current["rating"]
                metadata["userRatingTotal"] -= old_rating
            else:
                metadata["userRatingCount"] += 1

            metadata["userRatingTotal"] += review.rating
            metadata["userRatingAverage"] = round(
                metadata["userRatingTotal"] / metadata["userRatingCount"], 2
            )

            updated_review = {
                "user_id": user_id,
                "rating": review.rating,
                "review_text": review.review_text,
                "upvotes": current["upvotes"] if current else 0,
                "downvotes": current["downvotes"] if current else 0,
                "created_at": current["created_at"] if current else now.isoformat(),
                "updated_at": now.isoformat(),  # track when this review was last modified
            }

            review_data["reviews"][user_id] = updated_review
            ReviewRepository.save_review_data(movie_id, review_data)
            MovieRepository.save_movie_metadata(movie_id, metadata)

        return self._prepare_review_out(user_id, updated_review)

    def get_user_review(self, user_id: str, movie_id: str) -> Optional[ReviewOut]:
        """
        Return a user's review for a specific movie, or None if no review exists.
        """
        self._ensure_movie_exists(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        if user_id not in review_data["reviews"]:
            return None
        return self._prepare_review_out(user_id, review_data["reviews"][user_id])

    def upvote_review(self, movie_id: str, review_user_id: str, voter_user_id: str) -> ReviewOut:
        """
        Register an upvote. If the voter already upvoted, toggle it off. If they had a downvote, switch to upvote.
        """
        self._ensure_movie_exists(movie_id)
        with _REVIEW_RMW_LOCK:
            review_data = ReviewRepository.get_review_data(movie_id)
            reviews = review_data.get("reviews", {})
            if review_user_id not in reviews:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review not found")
            if review_user_id == voter_user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot upvote your own review")

            current = reviews[review_user_id]
            voters = current.get("voters", {})
            previous_vote = voters.get(voter_user_id)

            if previous_vote == "up":
                current["upvotes"] = max(0, int(current.get("upvotes") or 0) - 1)
                voters.pop(voter_user_id, None)
            elif previous_vote == "down":
                current["downvotes"] = max(0, int(current.get("downvotes") or 0) - 1)
                current["upvotes"] = int(current.get("upvotes") or 0) + 1
                voters[voter_user_id] = "up"
            else:
                current["upvotes"] = int(current.get("upvotes") or 0) + 1
                voters[voter_user_id] = "up"

            current["voters"] = voters
            current["updated_at"] = datetime.now(timezone.utc).isoformat()
            reviews[review_user_id] = current
            review_data["reviews"] = reviews
            ReviewRepository.save_review_data(movie_id, review_data)

        return self._prepare_review_out(review_user_id, current)

    def downvote_review(self, movie_id: str, review_user_id: str, voter_user_id: str) -> ReviewOut:
        """
        Register a downvote. If the voter already downvoted, toggle it off. If they had an upvote, switch to downvote.
        """
        self._ensure_movie_exists(movie_id)
        with _REVIEW_RMW_LOCK:
            review_data = ReviewRepository.get_review_data(movie_id)
            reviews = review_data.get("reviews", {})
            if review_user_id not in reviews:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review not found")
            if review_user_id == voter_user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot downvote your own review")

            current = reviews[review_user_id]
            voters = current.get("voters", {})
            previous_vote = voters.get(voter_user_id)

            if previous_vote == "down":
                current["downvotes"] = max(0, int(current.get("downvotes") or 0) - 1)
                voters.pop(voter_user_id, None)
            elif previous_vote == "up":
                current["upvotes"] = max(0, int(current.get("upvotes") or 0) - 1)
                current["downvotes"] = int(current.get("downvotes") or 0) + 1
                voters[voter_user_id] = "down"
            else:
                current["downvotes"] = int(current.get("downvotes") or 0) + 1
                voters[voter_user_id] = "down"

            current["voters"] = voters
            current["updated_at"] = datetime.now(timezone.utc).isoformat()
            reviews[review_user_id] = current
            review_data["reviews"] = reviews
            ReviewRepository.save_review_data(movie_id, review_data)

        return self._prepare_review_out(review_user_id, current)

    
    def delete_user_review(self, user_id: str, movie_id: str) -> None:
        """
        Delete a user's review for a movie and update the movie's rating metadata.
        """
        with _REVIEW_RMW_LOCK:
            self._ensure_movie_exists(movie_id)
            review_data = ReviewRepository.get_review_data(movie_id)

            if user_id not in review_data["reviews"]:
                return

        metadata = MovieRepository.get_movie_metadata(movie_id)
        # Ensure metadata has expected fields
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        current = review_data["reviews"][user_id]

        metadata["userRatingTotal"] -= current["rating"]
        metadata["userRatingCount"] -= 1
        if metadata["userRatingCount"] <= 0:
            metadata["userRatingCount"] = 0
            metadata["userRatingTotal"] = 0.0
            metadata["userRatingAverage"] = 0.0
        else:
            metadata["userRatingAverage"] = round(
                metadata["userRatingTotal"] / metadata["userRatingCount"], 2
            )

        del review_data["reviews"][user_id]

        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

    @staticmethod
    def get_reviews_by_user_id(user_id: str) -> Tuple[List[ReviewOut], List[str]]:
        """
        Collect all reviews authored by a user across all movies, returning both reviews and movie IDs.
        """
        reviews: List[ReviewOut] = []
        movies: List[str] = []
        all_movies = MovieRepository.list_movies()

        for movie in all_movies:
            movie_id = movie["id"]

            try:
                review_data = ReviewRepository.get_review_data(movie_id)
            except Exception as e:
                print(f"Warning: could not read reviews for {movie_id}: {e}")  # log and skip unreadable stores
                continue

            if not review_data or "reviews" not in review_data:
                continue

            if user_id in review_data["reviews"]:
                reviews.append(ReviewOut(**review_data["reviews"][user_id]))
                movies.append(movie_id)

        return reviews, movies
