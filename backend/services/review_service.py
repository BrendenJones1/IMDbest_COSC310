from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException, status

from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from repositories.movie_repo import MovieRepository, ReviewRepository


class ReviewService:

    def _ensure_movie_exists(self, movie_id: str):
        try:
            MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="movie not found")

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        self._ensure_movie_exists(movie_id)
        # Load movie metadata and reviews for this movie
        metadata = MovieRepository.get_movie_metadata(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        #Check if user already has a review for the movie
        current = review_data["reviews"].get(user_id)
        now = datetime.utcnow()

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
