import json
import os
import csv
from pathlib import Path
from typing import Any, Dict, Optional
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
    def _resolve_movie_dir(movie_id: str) -> Optional[Path]:
        """
        Locate the on-disk directory for a movie id, accepting raw ids or slugified titles.
        Returns None if no matching directory is found.
        """
        normalized = movie_id.strip().lower()
        direct_path = MOVIES_DIR / movie_id
        if direct_path.is_dir():
            return direct_path
        if not MOVIES_DIR.exists():
            return None
        for name in os.listdir(MOVIES_DIR):
            path = MOVIES_DIR / name
            if path.is_dir() and MovieRepository._slug(name) == normalized:
                return path
        return None

    @staticmethod
    def movie_exists(movie_id: str) -> bool:
        """Helper to check if a movie directory exists."""
        return MovieRepository._resolve_movie_dir(movie_id) is not None

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
            if not review_path.exists() or review_path.stat().st_size == 0:
                seeded = ReviewRepository._seed_from_csv_if_available(movie_id)
                if seeded is not None:
                    ReviewRepository.save_review_data(movie_id, {"reviews": seeded})
                    return {"reviews": seeded}
                return {"reviews": {}}

            with review_path.open("r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    seeded = ReviewRepository._seed_from_csv_if_available(movie_id)
                    if seeded is not None:
                        ReviewRepository.save_review_data(movie_id, {"reviews": seeded})
                        return {"reviews": seeded}
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

    @staticmethod
    def _seed_from_csv_if_available(movie_id: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to seed user_reviews.json from movieReviews.csv by picking top 10 reviews
        ranked by Usefulness Vote. Returns a reviews dict or None if CSV missing/unreadable.
        """
        movie_dir = MovieRepository._resolve_movie_dir(movie_id)
        if movie_dir is None:
            return None
        csv_path = movie_dir / "movieReviews.csv"
        if not csv_path.exists():
            return None

        try:
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = []
                for row in reader:
                    try:
                        upvotes = int(row.get("Usefulness Vote", 0) or 0)
                        total_votes = int(row.get("Total Votes", 0) or 0)
                        rating = float(row.get("User's Rating out of 10", 0) or 0)
                        username = (row.get("User") or "").strip() or "anonymous"
                        review_title = (row.get("Review Title") or "").strip()
                        review_body = (row.get("Review") or "").strip()
                        date_raw = (row.get("Date of Review") or "").strip()
                    except Exception:
                        continue

                    review_text = review_body
                    if review_title:
                        review_text = f"{review_title}\n\n{review_body}" if review_body else review_title

                    rows.append({
                        "user": username,
                        "upvotes": upvotes,
                        "total_votes": total_votes,
                        "rating": rating,
                        "review_text": review_text,
                        "date": date_raw,
                    })

                if not rows:
                    return None

                # Sort by usefulness vote desc, tie-breaker by total_votes desc
                rows.sort(key=lambda r: (r["upvotes"], r["total_votes"]), reverse=True)
                top = rows[:10]

                reviews: Dict[str, Any] = {}
                for item in top:
                    user_id = item["user"]
                    reviews[user_id] = {
                        "user_id": user_id,
                        "username": user_id,
                        "rating": item["rating"],
                        "review_text": item["review_text"],
                        "upvotes": item["upvotes"],
                        "downvotes": 0,
                        "created_at": item["date"] or None,
                        "updated_at": item["date"] or None,
                    }
                return reviews
        except Exception:
            return None

    @staticmethod
    def seed_all_from_csv(force_overwrite: bool = True) -> None:
        """
        Iterate over all movie directories and seed user_reviews.json from movieReviews.csv.
        If force_overwrite is True, existing review files are replaced.
        """
        if not MOVIES_DIR.exists():
            return
        for path in MOVIES_DIR.iterdir():
            if not path.is_dir():
                continue
            movie_id = MovieRepository._slug(path.name)
            target = path / "user_reviews.json"
            if target.exists() and not force_overwrite:
                continue
            seeded = ReviewRepository._seed_from_csv_if_available(movie_id)
            if seeded is not None:
                ReviewRepository.save_review_data(movie_id, {"reviews": seeded})


# Seed all review files from CSV on import (overwrite to ensure data present)
ReviewRepository.seed_all_from_csv(force_overwrite=True)
