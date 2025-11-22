import json
from pathlib import Path
from typing import Dict, Any

from repositories.movie_repo import MOVIES_DIR, MovieRepository


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


