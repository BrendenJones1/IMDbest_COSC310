from typing import Dict, Any

from backend.repositories.movie_repo import MovieRepository


class MoviesService:
    @staticmethod
    def get_metadata(movie_id: str) -> Dict[str, Any]:
        """
        Fetch movie metadata and normalize the shape for API responses.
        """
        meta = MovieRepository.get_movie_metadata(movie_id)
        user_rating_avg = meta.get("userRatingAverage")
        if user_rating_avg is None:
            user_rating_avg = meta.get("movieIMDbRating", 0.0)

        user_rating_count = meta.get("userRatingCount")
        if user_rating_count is None:
            user_rating_count = meta.get("totalRatingCount", 0)

        age_rating = meta.get("ageRating") or meta.get("contentRating") or meta.get("certificate")

        return {
            "movie_id": meta.get("movie_id", movie_id),
            "title": meta.get("title"),
            "poster": meta.get("poster"),
            "movieGenres": meta.get("movieGenres", []),
            "description": meta.get("description"),
            "ageRating": age_rating,
            "datePublished": meta.get("datePublished"),
            "userRatingAverage": float(user_rating_avg or 0.0),
            "userRatingCount": int(user_rating_count or 0),
            "movieIMDbRating": meta.get("movieIMDbRating"),
        }

