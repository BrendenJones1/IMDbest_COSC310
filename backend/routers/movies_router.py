from fastapi import APIRouter, Path
from typing import Dict, Any

from backend.services.movies_service import MoviesService

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/{movie_id}/metadata")
def get_movie_metadata(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
) -> Dict[str, Any]:
    """
    Return movie metadata including userRatingAverage and userRatingCount.
    """
    return MoviesService.get_metadata(movie_id)

