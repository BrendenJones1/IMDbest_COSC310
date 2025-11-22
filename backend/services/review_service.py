import json
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pathlib import Path

from fastapi import HTTPException, status

from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from repositories.movie_repo import MovieRepository
from repositories.reviews_repo import ReviewRepository


class ReviewService:

    def _parse_datetime(self, value):
        # Accept ISO strings, return datetime; fall back to current time if invalid
        if value is None:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value
        try:
            # fromisoformat handles most formats except 'Z' suffix; handle that
            text = str(value)
            if text.endswith("Z"):
                text = text[:-1]
            return datetime.fromisoformat(text)
        except Exception:
            return datetime.utcnow()

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
            created_raw = r.get("created_at") or r.get("timestamp") or r.get("updated_at")
            updated_raw = r.get("updated_at") or r.get("timestamp") or r.get("created_at")
            item = {
                "user_id": user_id,
                "username": r.get("username") or id_to_name.get(user_id),
                "rating": float(r.get("rating")) if r.get("rating") is not None else 0.0,
                "review_text": r.get("review_text"),
                "upvotes": int(r.get("upvotes") or 0),
                "downvotes": int(r.get("downvotes") or 0),
                "created_at": self._parse_datetime(created_raw),
                "updated_at": self._parse_datetime(updated_raw),
            }
            items.append(ReviewOut(**item))

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
        self._ensure_movie_exists(movie_id)
        # Load movie metadata and reviews for this movie
        metadata = MovieRepository.get_movie_metadata(movie_id)
        # Ensure metadata has expected fields (tests may create minimal metadata.json)
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        review_data = ReviewRepository.get_review_data(movie_id)

        #Check if user already has a review for the movie
        current = review_data["reviews"].get(user_id)
        now = datetime.now(timezone.utc)

        if current:
            # get rid of/update old reviews metadata
            old_rating = current["rating"]
            metadata["userRatingTotal"] -= old_rating
        else:
            # add total review count when review is created
            metadata["userRatingCount"] += 1

        #add and update rating
        metadata["userRatingTotal"] += review.rating
        metadata["userRatingAverage"] = round(
            metadata["userRatingTotal"] / metadata["userRatingCount"], 2
        )

        #create new, updated review
        updated_review = {
            "user_id": user_id,
            "rating": review.rating,
            "review_text": review.review_text,
            "upvotes": current["upvotes"] if current else 0,
            "downvotes": current["downvotes"] if current else 0,
            "created_at": current["created_at"] if current else now.isoformat(),
            "updated_at": now.isoformat()
        }

        #save review
        review_data["reviews"][user_id] = updated_review
        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

        
        return ReviewOut(**updated_review)

    def get_user_review(self, user_id: str, movie_id: str) -> Optional[ReviewOut]:
        self._ensure_movie_exists(movie_id)
        #get reviews
        review_data = ReviewRepository.get_review_data(movie_id)
        #check if user has a review for the movie
        if user_id not in review_data["reviews"]:
            return None
        return ReviewOut(**review_data["reviews"][user_id])

    def delete_user_review(self, user_id: str, movie_id: str) -> None:
        self._ensure_movie_exists(movie_id)
        # get reviews   
        review_data = ReviewRepository.get_review_data(movie_id)
        #check if user has a review for this movie: if not return, if they do continue
        if user_id not in review_data["reviews"]:
            return

        #get current metadata
        metadata = MovieRepository.get_movie_metadata(movie_id)
        # Ensure metadata has expected fields
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        current = review_data["reviews"][user_id]

        #subtract the user rating from total and update metadata
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

        # remove review
        del review_data["reviews"][user_id]

        #save review
        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

    def get_reviews_by_user_id(self, user_id: str) -> List[ReviewOut]:
        """
        Return all reviews authored by a given user_id,
        aggregated across all movies.
        """
        reviews: List[ReviewOut] = []
        movies: List[str] = []
        # Get all existing movies from the repo
        all_movies = MovieRepository.list_movies()
        
        for movie in all_movies:
            movie_id = movie['id']

            try:
                review_data = ReviewRepository.get_review_data(movie_id)
            except Exception as e:
                print(f"Warning: could not read reviews for {movie_id}: {e}")
                continue

            if not review_data or "reviews" not in review_data:
                continue

            # Each movie stores reviews keyed by user_id
            if user_id in review_data["reviews"]:
                reviews.append(ReviewOut(**review_data["reviews"][user_id]))
                movies.append(movie_id)

        return reviews, movies
