from fastapi import APIRouter, Path
from typing import Dict, Any

from backend.repositories.movie_repo import MovieRepository

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/{movie_id}/metadata")
def get_movie_metadata(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
) -> Dict[str, Any]:
    """
    Return movie metadata including userRatingAverage and userRatingCount.
    """
    meta = MovieRepository.get_movie_metadata(movie_id)
    # Ensure only relevant fields are present for this endpoint
    return {
        "movie_id": meta.get("movie_id", movie_id),
        "title": meta.get("title"),
        "userRatingAverage": meta.get("userRatingAverage", 0.0),
        "userRatingCount": meta.get("userRatingCount", 0),
    }

