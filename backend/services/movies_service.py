from typing import Dict, Any

from backend.repositories.movie_repo import MovieRepository


class MoviesService:
    @staticmethod
    def get_metadata(movie_id: str) -> Dict[str, Any]:
        """
        Fetch movie metadata and normalize the shape for API responses.
        """
        meta = MovieRepository.get_movie_metadata(movie_id)

        # Normalize numeric fields defensively
        def to_int(value, default=0):
            try:
                return int(value)
            except Exception:
                return default

        def to_float(value, default=0.0):
            try:
                return float(value)
            except Exception:
                return default

        return {
            "movie_id": meta.get("movie_id", movie_id),
            "title": meta.get("title"),
            "userRatingAverage": to_float(meta.get("userRatingAverage", 0.0)),
            "userRatingCount": to_int(meta.get("userRatingCount", meta.get("totalRatingCount", 0))),
            "movieIMDbRating": to_float(meta.get("movieIMDbRating", meta.get("imdbRating", 0.0))),
            "totalUserReviews": meta.get("totalUserReviews", meta.get("userReviews")),
            "totalRatingCount": meta.get("totalRatingCount"),
            "duration": meta.get("duration") or meta.get("runtime") or meta.get("movieDuration"),
            "datePublished": meta.get("datePublished"),
            "poster": meta.get("poster"),
            "description": meta.get("description"),
            "ageRating": meta.get("ageRating"),
            "movieGenres": meta.get("movieGenres"),
        }

