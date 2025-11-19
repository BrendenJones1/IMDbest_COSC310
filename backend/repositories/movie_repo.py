import json
from pathlib import Path
from typing import Any, Dict

# Absolute path to the movie data directory that ships with the backend
MOVIES_DIR = Path(__file__).resolve().parents[1] / "data" / "movies"

# Ensure the directory exists so tests can point this somewhere else
MOVIES_DIR.mkdir(parents=True, exist_ok=True)


class MovieRepository:

    @staticmethod
    def _slug(title):
    # very simple id: lowercase + spaces -> hyphens
        return title.strip().lower().replace(" ", "-")

    @staticmethod
    def _resolve_movie_dir(movie_id: str) -> Path:
        """
        Find the on-disk folder that matches the provided movie_id.
        The repository stores directories with their display titles,
        so we compare their slugified version.
        """
        normalized = movie_id.strip().lower()
        direct_path = MOVIES_DIR / movie_id
        if direct_path.is_dir():
            return direct_path

        if MOVIES_DIR.exists():
            for candidate in MOVIES_DIR.iterdir():
                if candidate.is_dir() and MovieRepository._slug(candidate.name) == normalized:
                    return candidate
        raise FileNotFoundError(f"Movie '{movie_id}' not found in {MOVIES_DIR}")

    @staticmethod
    def _metadata_path(movie_id: str) -> Path:
        try:
            movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            # Allow tests or new movies to automatically create a slug-based folder
            movie_dir = MOVIES_DIR / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
        return movie_dir / "metadata.json"

    @staticmethod
    def list_movies():
        items = []
        if not MOVIES_DIR.exists():
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
        metadata_path = MovieRepository._metadata_path(movie_id)
        if not metadata_path.exists():
            metadata = {}
        else:
            with metadata_path.open() as f:
                metadata = json.load(f)

        # ensure metadata has rating fields
        metadata.setdefault("movie_id", movie_id)
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        # load metadata from json file
        return metadata

    @staticmethod
    def save_movie_metadata(movie_id: str, metadata: Dict[str, Any]) -> None:
        metadata_path = MovieRepository._metadata_path(movie_id)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
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
        review_path = ReviewRepository._review_path(movie_id)
        if not review_path.exists():
            return {"reviews": {}}

        with review_path.open() as f:
            content = f.read().strip()
            if not content:
                return {"reviews": {}}
            payload = json.loads(content)

        if isinstance(payload, dict) and "reviews" in payload and isinstance(payload["reviews"], dict):
            return {"reviews": payload["reviews"]}
        if isinstance(payload, dict):
            return {"reviews": payload}
        raise ValueError("Review data must be a JSON object")

    @staticmethod
    def save_review_data(movie_id: str, data: Dict[str, Any]) -> None:
        review_path = ReviewRepository._review_path(movie_id)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        with review_path.open("w") as f:
            json.dump({"reviews": data.get("reviews", {})}, f, indent=2)
