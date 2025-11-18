from pathlib import Path
import json
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.routers.reviews_router import router as reviews_router
from backend.repositories.movie_repo import MovieRepository

#use: pytest backend/tests/test_review_sorting.py -v 
#to see test output
app = FastAPI()
app.include_router(reviews_router)
client = TestClient(app)


def _movie_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "backend" / "data" / "movies" / "Test Movie Sorting"


def setup_module(module=None):
    # Create a test movie with three reviews
    mdir = _movie_dir()
    mdir.mkdir(parents=True, exist_ok=True)
    reviews_path = mdir / "user_reviews.json"

    now = datetime.now(timezone.utc)
    data = {
        "user-a": {
            "rating": 7,
            "review_text": "ok",
            "upvotes": 5,
            "downvotes": 1,
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": (now - timedelta(hours=12)).isoformat(),
        },
        "user-b": {
            "rating": 9,
            "review_text": "great",
            "upvotes": 10,
            "downvotes": 0,
            "created_at": (now - timedelta(days=2)).isoformat(),
            "updated_at": (now - timedelta(days=1, hours=1)).isoformat(),
        },
        "user-c": {
            "rating": 6,
            "review_text": "meh",
            "upvotes": 2,
            "downvotes": 3,
            "created_at": (now - timedelta(hours=6)).isoformat(),
            "updated_at": (now - timedelta(hours=6)).isoformat(),
        },
    }
    with open(reviews_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def teardown_module(module=None):
    # Remove the test directory and file
    mdir = _movie_dir()
    if mdir.exists():
        for p in mdir.iterdir():
            p.unlink()
        mdir.rmdir()


def test_list_reviews_sort_by_upvotes():
    # slug for "Test Movie Sorting"
    movie_id = MovieRepository._slug("Test Movie Sorting")
    r = client.get(f"/reviews/{movie_id}?sort=upvotes")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    usernames = [item["user_id"] for item in data["items"]]
    # user-b has 10 upvotes, then user-a (5), then user-c (2)
    assert usernames == ["user-b", "user-a", "user-c"]


def test_list_reviews_sort_by_recent():
    movie_id = MovieRepository._slug("Test Movie Sorting")
    r = client.get(f"/reviews/{movie_id}?sort=recent")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    usernames = [item["user_id"] for item in data["items"]]
    # user-c is most recent (6 hours ago), then user-a (~1 day), then user-b (~2 days)
    assert usernames == ["user-c", "user-a", "user-b"]


def test_top_reviews_with_limit_and_total():
    movie_id = MovieRepository._slug("Test Movie Sorting")
    # default sort is upvotes; request only top 2
    r = client.get(f"/reviews/{movie_id}?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    usernames = [item["user_id"] for item in data["items"]]
    assert usernames == ["user-b", "user-a"]


def test_see_all_reviews_with_large_limit():
    movie_id = MovieRepository._slug("Test Movie Sorting")
    r = client.get(f"/reviews/{movie_id}?sort=upvotes&limit=100")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    usernames = [item["user_id"] for item in data["items"]]
    assert usernames == ["user-b", "user-a", "user-c"]

