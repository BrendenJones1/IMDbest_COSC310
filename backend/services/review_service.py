from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status

from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from repositories.movie_repo import MovieRepository, ReviewRepository
from repositories.users_repo import UserRepository, user_repository


class ReviewService:
    def __init__(self, user_repo: Optional[UserRepository] = None) -> None:
        self.user_repo = user_repo or user_repository

    def _parse_datetime(self, value: Optional[Any]) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if isinstance(value, datetime):
            return value
        try:
            text = str(value)
            if text.endswith("Z"):
                text = text[:-1]
            return datetime.fromisoformat(text)
        except Exception:
            return datetime.now(timezone.utc)

    def _ensure_movie_exists(self, movie_id: str):
        if not MovieRepository.movie_exists(movie_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="movie not found",
            )

    def list_reviews(self, movie_id: str, sort: str = "recent"):
        """
        Return list of serialized review dicts for a movie sorted by upvotes or recency.
        """
        self._ensure_movie_exists(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id) or {}
        reviews_map = review_data.get("reviews", {})

        try:
            users = self.user_repo.load_users() or []
        except Exception:
            users = []
        usernames = {user.get("id"): user.get("username") for user in users}

        items: List[Dict[str, Any]] = []
        for user_id, raw in reviews_map.items():
            created_raw = raw.get("created_at") or raw.get("timestamp")
            updated_raw = raw.get("updated_at") or raw.get("timestamp") or raw.get("created_at")
            payload = {
                "user_id": user_id,
                "rating": float(raw.get("rating") or 0),
                "review_text": raw.get("review_text"),
                "upvotes": int(raw.get("upvotes") or 0),
                "downvotes": int(raw.get("downvotes") or 0),
                "created_at": self._parse_datetime(created_raw),
                "updated_at": self._parse_datetime(updated_raw),
            }
            review_out = ReviewOut(**payload)
            review_dict = review_out.model_dump()
            review_dict["username"] = usernames.get(user_id, user_id)
            items.append(review_dict)

        if sort == "upvotes":
            items.sort(key=lambda item: (item["upvotes"], item["created_at"]), reverse=True)
        else:
            items.sort(key=lambda item: item["created_at"], reverse=True)
        return items

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        self._ensure_movie_exists(movie_id)
        # Load movie metadata and reviews for this movie
        metadata = MovieRepository.get_movie_metadata(movie_id)
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
        current = review_data["reviews"][user_id]

        #subtract the user rating from total and update metadata
        metadata["userRatingTotal"] -= current["rating"]
        metadata["userRatingCount"] -= 1
        metadata["userRatingAverage"] = (
            round(metadata["userRatingTotal"] / metadata["userRatingCount"], 2)
            if metadata["userRatingCount"] > 0 else 0.0
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
