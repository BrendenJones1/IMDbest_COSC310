import json
from pathlib import Path
from typing import Any, Dict, List

# Backing data lives under backend/data/movies
MOVIES_DIR = Path(__file__).resolve().parents[1] / "data" / "movies"
MOVIES_DIR.mkdir(parents=True, exist_ok=True)


class MovieRepository:

    @staticmethod
    def _slug(title: str) -> str:
        # very simple id: lowercase + spaces -> hyphens
        return title.strip().lower().replace(" ", "-")

    @staticmethod
    def _resolve_movie_dir(movie_id: str) -> Path:
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
            movie_dir = MOVIES_DIR / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
        return movie_dir / "metadata.json"

    @staticmethod
    def _load_metadata_file(metadata_path: Path, movie_id: str) -> Dict[str, Any]:
        if metadata_path.exists():
            with metadata_path.open() as f:
                metadata = json.load(f)
        else:
            metadata = {}
        metadata.setdefault("movie_id", movie_id)
        metadata.setdefault("title", metadata.get("title") or movie_id.replace("-", " ").title())
        metadata.setdefault("userRatingCount", 0)
        metadata.setdefault("userRatingTotal", 0.0)
        metadata.setdefault("userRatingAverage", 0.0)
        metadata.setdefault("movieIMDbRating", 0.0)
        metadata.setdefault("datePublished", "")
        return metadata

    @staticmethod
    def list_movies(include_metadata: bool = False) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if not MOVIES_DIR.exists():
            return items
        for path in sorted(MOVIES_DIR.iterdir(), key=lambda p: p.name.lower()):
            if not path.is_dir():
                continue
            movie_id = MovieRepository._slug(path.name)
            metadata = MovieRepository._load_metadata_file(path / "metadata.json", movie_id)
            item = {
                "id": movie_id,
                "title": metadata.get("title") or path.name,
            }
            if include_metadata:
                item["metadata"] = metadata
            items.append(item)
        return items

    @staticmethod
    def search_movies(q: str, include_metadata: bool = False) -> List[Dict[str, Any]]:
        if not q or not q.strip():
            return MovieRepository.list_movies(include_metadata=include_metadata)
        q = q.strip().lower()
        results = []
        for movie in MovieRepository.list_movies(include_metadata=include_metadata):
            title = (movie.get("title") or "").lower()
            if q in title:
                results.append(movie)
        return results

    @staticmethod
    def get_movie_metadata(movie_id: str) -> Dict[str, Any]:
        metadata_path = MovieRepository._metadata_path(movie_id)
        return MovieRepository._load_metadata_file(metadata_path, movie_id)

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
            payload = json.load(f)
        if isinstance(payload, dict) and "reviews" in payload and isinstance(payload["reviews"], dict):
            return {"reviews": payload["reviews"]}
        if isinstance(payload, dict):
            return {"reviews": payload}
        raise ValueError("Review data must be stored as a JSON object")

    @staticmethod
    def save_review_data(movie_id: str, data: Dict[str, Any]) -> None:
        review_path = ReviewRepository._review_path(movie_id)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        with review_path.open("w") as f:
            json.dump({"reviews": data.get("reviews", {})}, f, indent=2)
