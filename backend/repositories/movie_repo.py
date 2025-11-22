import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


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
    def movie_exists(movie_id: str) -> bool:
        # helper method to check if movie exists
        return MovieRepository._resolve_movie_dir(movie_id) is not None

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
    def _metadata_path(movie_id: str) -> Path:
        """
        Compute the metadata.json path for a given movie id (slug).
        Does not create directories; callers decide persistence.
        """
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            return MOVIES_DIR / movie_id / "metadata.json"
        return movie_dir / "metadata.json"

    @staticmethod
    def _load_metadata_file(metadata_path: Path, movie_id: str) -> Dict[str, Any]:
        """
        Load metadata from the given path, applying stable defaults when missing.
        """
        if metadata_path.exists():
            with metadata_path.open() as f:
                metadata = json.load(f) or {}
        else:
            metadata = {}
        metadata.setdefault("movie_id", movie_id)
        metadata.setdefault("title", metadata.get("title") or movie_id.replace("-", " ").title())
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        # Optional fields that other features/tests may use
        metadata.setdefault("movieIMDbRating", 0.0)
        metadata.setdefault("datePublished", "")
        return metadata

    @staticmethod
    def list_movies(include_metadata: bool = False):
        items = []
        if not os.path.isdir(MOVIES_DIR):
            return items
        for path in sorted(MOVIES_DIR.iterdir(), key=lambda p: p.name.lower()):
            if path.is_dir():
                items.append({
                    "id": MovieRepository._slug(path.name),
                    "title": path.name
                })
        return items

    @staticmethod
    def search_movies(q: str, include_metadata: bool = False):
        """
        Search movies by substring in the title. If q is empty, return all movies.
        When include_metadata is True, each result will include a 'metadata' key
        populated from the movie's metadata.json.
        """
        query = (q or "").strip().lower()
        candidates = MovieRepository.list_movies()
        if query:
            candidates = [
                m for m in candidates
                if query in (m.get("title") or "").lower()
            ]

        if not include_metadata:
            return candidates

        results = []
        for movie in candidates:
            metadata = MovieRepository.get_movie_metadata(movie["id"])
            results.append({**movie, "metadata": metadata})
        return results

    @staticmethod
    def get_movie_metadata(movie_id: str) -> Dict[str, Any]:
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        metadata_path = (
            movie_dir / "metadata.json"
            if movie_dir is not None
            else MOVIES_DIR / movie_id / "metadata.json"
        )
        return MovieRepository._load_metadata_file(metadata_path, movie_id)

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
    def _review_path(movie_id: str) -> Path:
        try:
            movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            movie_dir = MOVIES_DIR / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
        return movie_dir / "user_reviews.json"

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
