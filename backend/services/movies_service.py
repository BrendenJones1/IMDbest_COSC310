from typing import Dict, Any

from backend.repositories.movie_repo import MovieRepository


class MoviesService:
    @staticmethod
    def get_metadata(movie_id: str) -> Dict[str, Any]:
        """
        Fetch movie metadata and normalize the shape for API responses.
        """
        meta = MovieRepository.get_movie_metadata(movie_id)
        return {
            "movie_id": meta.get("movie_id", movie_id),
            "title": meta.get("title"),
            "userRatingAverage": float(meta.get("userRatingAverage", 0.0)),
            "userRatingCount": int(meta.get("userRatingCount", 0)),
        }


