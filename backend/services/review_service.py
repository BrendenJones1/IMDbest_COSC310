from datetime import datetime, timezone
from typing import Optional, Tuple, List

# Prefer backend.* schema types (matches tests' imports); fall back to local.
try:  # pragma: no cover
    from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut  # type: ignore
except ImportError:  # pragma: no cover
    from schemas.review import ReviewCreate, ReviewUpdate, ReviewOut  # type: ignore

# Prefer local repositories so pytest monkeypatches against repositories.* apply; fall back to backend.*.
try:  # pragma: no cover
    from repositories.movie_repo import MovieRepository, ReviewRepository  # type: ignore
except ImportError:  # pragma: no cover
    from backend.repositories.movie_repo import MovieRepository, ReviewRepository  # type: ignore


class ReviewService:

    def upsert_review(self, user_id: str, movie_id: str, review: ReviewCreate) -> ReviewOut:
        # Load movie metadata and reviews for this movie
        metadata = MovieRepository.get_movie_metadata(movie_id)
        review_data = ReviewRepository.get_review_data(movie_id)

        #Check if user already has a review for the movie
        current = review_data["reviews"].get(user_id)
        now = datetime.now(timezone.utc)

        rating_total = float(metadata.get("userRatingTotal", 0.0))
        rating_count = int(metadata.get("userRatingCount", 0))

        if current:
            # get rid of/update old reviews metadata
            rating_total -= float(current["rating"])
        else:
            # add total review count when review is created
            rating_count += 1

        #add and update rating
        rating_total += float(review.rating)
        rating_total = max(rating_total, 0.0)

        metadata["userRatingTotal"] = round(rating_total, 3)
        metadata["userRatingCount"] = rating_count
        metadata["userRatingAverage"] = round(
            rating_total / rating_count, 2
        ) if rating_count else 0.0

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
        #get reviews
        review_data = ReviewRepository.get_review_data(movie_id)
        #check if user has a review for the movie
        if user_id not in review_data["reviews"]:
            return None
        return ReviewOut(**review_data["reviews"][user_id])

    def delete_user_review(self, user_id: str, movie_id: str) -> None:
        # get reviews
        review_data = ReviewRepository.get_review_data(movie_id)
        #check if user has a review for this movie: if not return, if they do continue
        if user_id not in review_data["reviews"]:
            return

        #get current metadata
        metadata = MovieRepository.get_movie_metadata(movie_id)
        current = review_data["reviews"][user_id]

        #subtract the user rating from total and update metadata
        rating_total = float(metadata.get("userRatingTotal", 0.0)) - float(current["rating"])
        rating_total = max(rating_total, 0.0)
        rating_count = max(int(metadata.get("userRatingCount", 0)) - 1, 0)
        metadata["userRatingTotal"] = round(rating_total, 3)
        metadata["userRatingCount"] = rating_count
        metadata["userRatingAverage"] = round(rating_total / rating_count, 2) if rating_count else 0.0

        # remove review
        del review_data["reviews"][user_id]

        #save review
        ReviewRepository.save_review_data(movie_id, review_data)
        MovieRepository.save_movie_metadata(movie_id, metadata)

    def get_reviews_by_user_id(self, user_id: str) -> Tuple[List[ReviewOut], List[str]]:
        """Return all reviews written by a user across all movies."""
        reviews: List[ReviewOut] = []
        movie_ids: List[str] = []

        for movie in MovieRepository.list_movies():
            movie_id = movie["id"]
            review_data = ReviewRepository.get_review_data(movie_id)
            user_review = review_data.get("reviews", {}).get(user_id)
            if user_review:
                reviews.append(ReviewOut(**user_review))
                movie_ids.append(movie_id)

        return reviews, movie_ids
