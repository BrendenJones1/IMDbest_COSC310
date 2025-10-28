# backend/services/search_service.py
from backend.repositories.movie_repo import search_movies


def search(q, limit=20):
    if not q:
        return []
    results = search_movies(q)
    return results[:limit]
