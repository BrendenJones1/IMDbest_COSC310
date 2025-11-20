from datetime import datetime
from typing import Optional, List, Tuple

from fastapi import HTTPException, status

from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from repositories.movie_repo import MovieRepository, ReviewRepository


class ReviewService:
    """
    Provide high-level operations for creating, updating, and deleting movie reviews.
    """

    def _ensure_movie_exists(self, movie_id: str):
        """
        Raise a 404 HTTP error if the given movie_id does not correspond to a stored movie.
        """
        try:
            MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="movie not found")

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        """
        Create or update a user's review for a movie and keep aggregated rating metadata in sync.
        """
        self._ensure_movie_exists(movie_id)
        metadata = MovieRepository.get_movie_metadata(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        current = review_data["reviews"].get(user_id)
        now = datetime.utcnow()

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

        return ReviewOut(**updated_review)

    def get_user_review(self, user_id: str, movie_id: str) -> Optional[ReviewOut]:
        """
        Return a user's review for a specific movie, or None if no review exists.
        """
        self._ensure_movie_exists(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        if user_id not in review_data["reviews"]:
            return None
        return ReviewOut(**review_data["reviews"][user_id])

    def delete_user_review(self, user_id: str, movie_id: str) -> None:
        """
        Delete a user's review for a movie and update the movie's rating metadata.
        """
        self._ensure_movie_exists(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        if user_id not in review_data["reviews"]:
            return

        metadata = MovieRepository.get_movie_metadata(movie_id)
        current = review_data["reviews"][user_id]

        metadata["userRatingTotal"] -= current["rating"]
        metadata["userRatingCount"] -= 1
        metadata["userRatingAverage"] = (
            round(metadata["userRatingTotal"] / metadata["userRatingCount"], 2)
            if metadata["userRatingCount"] > 0
            else 0.0
        )

        del review_data["reviews"][user_id]

        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

    def get_reviews_by_user_id(self, user_id: str) -> Tuple[List[ReviewOut], List[str]]:
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
