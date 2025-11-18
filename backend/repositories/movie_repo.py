import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


# config directories (point to backend/data/movies)
MOVIES_DIR = Path(__file__).resolve().parents[1] / "data" / "movies"

# Make sure the directories exist
MOVIES_DIR.mkdir(parents=True, exist_ok=True)


class MovieRepository:

    @staticmethod
    def _slug(title):
        # very simple id: lowercase + spaces -> hyphens
        return title.strip().lower().replace(" ", "-")

    @staticmethod
    def _resolve_movie_dir(movie_id: str) -> Optional[Path]:
        """
        Resolve a movie directory from a given slugged movie_id.
        Returns None if no matching directory is found.
        """
        if not MOVIES_DIR.exists():
            return None
        for name in os.listdir(MOVIES_DIR):
            path = MOVIES_DIR / name
            if path.is_dir() and MovieRepository._slug(name) == movie_id:
                return path
        return None

    @staticmethod
    def list_movies():
        items = []
        if not os.path.isdir(MOVIES_DIR):
            return items
        for name in sorted(os.listdir(MOVIES_DIR)):
            path = os.path.join(MOVIES_DIR, name)
            if os.path.isdir(path):
                items.append({
                    "id": MovieRepository._slug(name),
                    "title": name
                })
        return items

    @staticmethod
    def search_movies(q):
        if not q:
            return []
        q = q.strip().lower()
        results = []
        for m in MovieRepository.list_movies():
            title = (m.get("title") or "").lower()
            if q in title:
                results.append(m)
        return results

    @staticmethod
    def get_movie_metadata(movie_id: str) -> Dict[str, Any]:
        # Resolve the folder for this movie id
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            # Return default metadata if movie folder doesn't exist
            return {
                "movie_id": movie_id,
                "userRatingCount": 0,
                "userRatingTotal": 0,
                "userRatingAverage": 0.0
            }
        metadata_path = movie_dir / "metadata.json"
        if not metadata_path.exists():
            return {
                "movie_id": movie_id,
                "userRatingCount": 0,
                "userRatingTotal": 0,
                "userRatingAverage": 0.0
            }
        with metadata_path.open() as f:
            return json.load(f)

    @staticmethod
    def save_movie_metadata(movie_id: str, metadata: Dict[str, Any]) -> None:
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        # If movie directory doesn't exist, we will not create a new one here.
        # In this project, movies are pre-seeded.
        if movie_dir is None:
            return
        metadata_path = movie_dir / "metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)


class ReviewRepository:
    @staticmethod
    def get_review_data(movie_id: str) -> Dict[str, Any]:
        # find review data path by resolving the movie directory
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            return {"reviews": {}}
        review_path = movie_dir / "user_reviews.json"
        if not review_path.exists() or review_path.stat().st_size == 0:
            return {"reviews": {}}
        with review_path.open() as f:
            data = json.load(f)
            # Support both dict of reviews and raw mapping at top-level
            if isinstance(data, dict) and "reviews" in data:
                return data
            if isinstance(data, dict):
                return {"reviews": data}
            return {"reviews": {}}

    @staticmethod
    def save_review_data(movie_id: str, data: Dict[str, Any]) -> None:
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            return
        review_path = movie_dir / "user_reviews.json"
        # normalize shape
        to_write = data if "reviews" in data else {"reviews": data}
        with review_path.open("w") as f:
            json.dump(to_write, f, indent=2)