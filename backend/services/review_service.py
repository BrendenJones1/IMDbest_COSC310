from datetime import datetime
from typing import Dict, Optional, Tuple

# Prefer backend.* schema to align with tests; fall back to local if needed
try:  # pragma: no cover
    from backend.schemas.review import ReviewCreate, ReviewOut  # type: ignore
except ImportError:  # pragma: no cover
    from schemas.review import ReviewCreate, ReviewOut  # type: ignore

# Prefer local repos so monkeypatching works in tests; fall back to backend.*.
try:  # pragma: no cover
    from repositories.movie_repo import MovieRepository, ReviewRepository  # type: ignore
except ImportError:  # pragma: no cover
    from backend.repositories.movie_repo import MovieRepository, ReviewRepository  # type: ignore


class ReviewService:
    """Business logic for creating, retrieving, and deleting movie reviews."""

    @staticmethod
    def _calculate_average(total_rating: float, total_count: int) -> float:
        if total_count <= 0:
            return 0.0
        return round(total_rating / total_count, 2)

    @staticmethod
    def _load_state(movie_id: str) -> Tuple[Dict, Dict]:
        metadata = MovieRepository.get_movie_metadata(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)
        review_data.setdefault("reviews", {})
        return metadata, review_data

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        metadata, review_data = self._load_state(movie_id)
        current = review_data["reviews"].get(user_id)
        now = datetime.utcnow().isoformat()

        if current:
            metadata["userRatingTotal"] -= current["rating"]
        else:
            metadata["userRatingCount"] += 1

        metadata["userRatingTotal"] += review.rating
        metadata["userRatingAverage"] = self._calculate_average(
            metadata["userRatingTotal"], metadata["userRatingCount"]
        )

        updated_review = {
            "user_id": user_id,
            "rating": review.rating,
            "review_text": review.review_text,
            "upvotes": current["upvotes"] if current else 0,
            "downvotes": current["downvotes"] if current else 0,
            "created_at": current["created_at"] if current else now,
            "updated_at": now,
        }

        review_data["reviews"][user_id] = updated_review
        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)
        return ReviewOut(**updated_review)

    def get_user_review(self, user_id: str, movie_id: str) -> Optional[ReviewOut]:
        _, review_data = self._load_state(movie_id)
        user_review = review_data["reviews"].get(user_id)
        return ReviewOut(**user_review) if user_review else None

    def delete_user_review(self, user_id: str, movie_id: str) -> None:
        metadata, review_data = self._load_state(movie_id)
        current = review_data["reviews"].get(user_id)
        if not current:
            return

        metadata["userRatingTotal"] -= current["rating"]
        metadata["userRatingCount"] = max(metadata["userRatingCount"] - 1, 0)
        metadata["userRatingAverage"] = self._calculate_average(
            metadata["userRatingTotal"], metadata["userRatingCount"]
        )

        del review_data["reviews"][user_id]
        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

    def get_reviews_by_user_id(self, user_id: str) -> Tuple[list[ReviewOut], list[str]]:
        """Return all reviews by a user across all movies."""
        reviews: list[ReviewOut] = []
        movie_ids: list[str] = []

        for movie in MovieRepository.list_movies():
            movie_id = movie.get("id") or movie.get("title")
            if not movie_id:
                continue
            review_data = ReviewRepository.get_review_data(movie_id)
            user_review = (review_data.get("reviews") or {}).get(user_id)
            if user_review:
                reviews.append(ReviewOut(**user_review))
                movie_ids.append(movie_id)

        return reviews, movie_ids
