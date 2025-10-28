import json
import os
from pathlib import Path
from typing import Dict, Any


#config directories
MOVIES_DIR = Path("app/data/movies")

#Make sure the directories exist
MOVIES_DIR.mkdir(parents=True, exist_ok=True)


class MovieRepository:


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

    @staticmethod
    def get_movie_metadata(movie_id: str) -> Dict[str, Any]:
        # find metadata path
        metadata_path = MOVIES_DIR / f"{movie_id}.json"
        # If metadata file doesnt exist, return default empty structure
        if not metadata_path.exists():
            return {
                "movie_id": movie_id,
                "userRatingCount": 0,
                "userRatingTotal": 0,
                "userRatingAverage": 0.0
            }
        # load metadata from json file
        with metadata_path.open() as f:
            return json.load(f)

    @staticmethod
    def save_movie_metadata(movie_id: str, metadata: Dict[str, Any]) -> None:
        # find metadata path
        metadata_path = MOVIES_DIR / f"{movie_id}.json"
        # write metadata to json file
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)


class ReviewRepository:
    @staticmethod
    def get_review_data(movie_id: str) -> Dict[str, Any]:
        # find review data path
        review_path = MOVIES_DIR / movie_id / "user_reviews.json"
        # return empty if no reviews yet
        if not review_path.exists():
            return {"reviews": {}}
        # load review data
        with review_path.open() as f:
            return json.load(f)

    @staticmethod
    def save_review_data(movie_id: str, data: Dict[str, Any]) -> None:
        #save review data back to the file
        review_path = MOVIES_DIR / movie_id / "user_reviews.json"
        with review_path.open("w") as f:
            json.dump(data, f, indent=2)
