import json
import os
from pathlib import Path
from typing import Any, Dict
from threading import RLock  # NEW: for repo-level concurrency


# config directories (point to backend/data/movies)
MOVIES_DIR = Path(__file__).resolve().parents[1] / "data" / "movies"

# Make sure the directories exist
MOVIES_DIR.mkdir(parents=True, exist_ok=True)

# NEW: locks to protect movie metadata and review files
_MOVIE_METADATA_LOCK = RLock()
_REVIEW_DATA_LOCK = RLock()


class MovieRepository:

    @staticmethod
    def _slug(title):
        """
        Generate a simple, stable identifier from a movie title.
        """
        return title.strip().lower().replace(" ", "-")

    
    @staticmethod
    def _resolve_movie_dir(movie_id: str) -> Path:
        """
        Locate the on-disk directory for a movie id, accepting raw ids or slugified titles.
        """
        normalized = movie_id.strip().lower()
        direct_path = MOVIES_DIR / movie_id
        if direct_path.is_dir():
            return direct_path
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
        Resolve the path to a movie's metadata.json, creating its directory on demand.
        """
        try:
            movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            # Allow tests or new movies to automatically create a slug-based folder
            movie_dir = MOVIES_DIR / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
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
        Search movies by partial title, optionally returning metadata for each match.
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
        """
        Load stored metadata for a movie and ensure rating fields are always present.
        Protected by a lock to avoid concurrent read/write races.
        """
        metadata_path = MovieRepository._metadata_path(movie_id)

        with _MOVIE_METADATA_LOCK:
            if not metadata_path.exists():
                metadata = {}
            else:
                with metadata_path.open("r", encoding="utf-8") as f:
                    metadata = json.load(f)

        metadata.setdefault("movie_id", movie_id)
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        return metadata

    @staticmethod
    def save_movie_metadata(movie_id: str, metadata: Dict[str, Any]) -> None:
        """
        Persist metadata for a movie to its on-disk metadata.json file.
        Writes are atomic via a temp file + os.replace and protected by a lock.
        """
        metadata_path = MovieRepository._metadata_path(movie_id)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = metadata_path.with_name(metadata_path.name + ".tmp")

        with _MOVIE_METADATA_LOCK:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            os.replace(tmp_path, metadata_path)


class ReviewRepository:
    @staticmethod
    def _review_path(movie_id: str) -> Path:
        """
        Resolve the path to a movie's user_reviews.json, creating its directory if needed.
        """
        try:
            movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        except FileNotFoundError:
            movie_dir = MOVIES_DIR / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
        return movie_dir / "user_reviews.json"

    @staticmethod
    def get_review_data(movie_id: str) -> Dict[str, Any]:
        """
        Load user review data for a movie and normalize it to a {'reviews': {...}} structure.
        Protected by a lock to avoid concurrent read/write races.
        """
        review_path = ReviewRepository._review_path(movie_id)

        with _REVIEW_DATA_LOCK:
            if not review_path.exists():
                return {"reviews": {}}

            with review_path.open("r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {"reviews": {}}
                payload = json.loads(content)

        # Accept both wrapped and legacy flat JSON formats for stored reviews.
        if isinstance(payload, dict) and "reviews" in payload and isinstance(payload["reviews"], dict):
            return {"reviews": payload["reviews"]}
        if isinstance(payload, dict):
            return {"reviews": payload}
        raise ValueError("Review data must be a JSON object")

    @staticmethod
    def save_review_data(movie_id: str, data: Dict[str, Any]) -> None:
        """
        Persist normalized review data for a movie to its user_reviews.json file.
        Writes are atomic via a temp file + os.replace and protected by a lock.
        """
        review_path = ReviewRepository._review_path(movie_id)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = review_path.with_name(review_path.name + ".tmp")

        with _REVIEW_DATA_LOCK:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump({"reviews": data.get("reviews", {})}, f, indent=2)
            os.replace(tmp_path, review_path)
