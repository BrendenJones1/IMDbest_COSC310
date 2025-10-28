# backend/repositories/movie_repo.py
import os

# movies 目录：backend/data/movies
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVIES_DIR = os.path.join(BASE_DIR, "data", "movies")

def _slug(title):
    # very simple id: lowercase + spaces -> hyphens
    return title.strip().lower().replace(" ", "-")

def list_movies():
    items = []
    if not os.path.isdir(MOVIES_DIR):
        return items
    for name in sorted(os.listdir(MOVIES_DIR)):
        path = os.path.join(MOVIES_DIR, name)
        if os.path.isdir(path):
            items.append({
                "id": _slug(name),
                "title": name
            })
    return items

def search_movies(q):
    if not q:
        return []
    q = q.strip().lower()
    results = []
    for m in list_movies():
        title = (m.get("title") or "").lower()
        if q in title:
            results.append(m)
    return results
