# backend/services/search_service.py
from enum import Enum
from typing import Any, Dict, List

from backend.repositories.movie_repo import MovieRepository


class SortField(str, Enum):
    """
    Supported fields that search results can be sorted by.
    """
    TITLE = "title"
    IMDB_RATING = "imdb_rating"
    USER_RATING = "user_rating"
    RELEASE_DATE = "release_date"


class SortOrder(str, Enum):
    """
    Allowed sort directions for search results.
    """
    ASC = "asc"
    DESC = "desc"


def _sort_key(movie: Dict[str, Any], sort_by: SortField):
    """
    Derive a normalized sort key for a movie based on the requested sort field.
    """
    metadata = movie.get("metadata") or {}
    if sort_by == SortField.IMDB_RATING:
        return float(metadata.get("movieIMDbRating") or 0.0)
    if sort_by == SortField.USER_RATING:
        return float(metadata.get("userRatingAverage") or 0.0)
    if sort_by == SortField.RELEASE_DATE:
        return metadata.get("datePublished") or ""
    return (movie.get("title") or "").lower()


def _present_movie(movie: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shape a raw movie record into the public search result representation.
    """
    metadata = movie.get("metadata") or {}
    return {
        "id": movie["id"],
        "title": movie["title"],
        "imdbRating": metadata.get("movieIMDbRating"),
        "userRatingAverage": metadata.get("userRatingAverage"),
        "releaseDate": metadata.get("datePublished"),
    }


def search(
    q: str,
    limit: int = 20,
    sort_by: SortField = SortField.TITLE,
    sort_order: SortOrder = SortOrder.ASC,
) -> List[Dict[str, Any]]:
    """
    Search movies by query string and return a sorted, limited list of result summaries.
    """
    limit = max(1, min(limit, 50))  # enforce a safe, bounded page size
    results = MovieRepository.search_movies(q, include_metadata=True)
    reverse = sort_order == SortOrder.DESC
    sorted_results = sorted(results, key=lambda m: _sort_key(m, sort_by), reverse=reverse)
    return [_present_movie(movie) for movie in sorted_results[:limit]]
