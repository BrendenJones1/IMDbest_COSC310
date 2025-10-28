# backend/services/search_service.py
from backend.repositories.movie_repo import MovieRepository


def search(q, limit=20):
    if not q:
        return []
    results = MovieRepository.search_movies(q)
    return results[:limit]
