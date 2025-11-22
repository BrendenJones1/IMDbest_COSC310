from pathlib import Path
import json
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.main import app
from backend.repositories.movie_repo import MovieRepository

#use: pytest backend/tests/test_review_sorting.py -v 
#to see test output
import sys
from pathlib import Path as _P
# Ensure project root is on sys.path so 'backend' package can be imported
sys.path.append(str(_P(__file__).resolve().parents[2]))
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


def test_sort_upvotes_tie_breaks_by_recent():
    # Create a separate movie where two reviews have equal upvotes but different recency
    title = "Test Sorting Ties Upvotes"
    mdir = Path(__file__).resolve().parents[2] / "backend" / "data" / "movies" / title
    mdir.mkdir(parents=True, exist_ok=True)
    try:
        reviews_path = mdir / "user_reviews.json"
        now = datetime.now(timezone.utc)
        data = {
            "user-old": {
                "rating": 5,
                "review_text": "old",
                "upvotes": 5,
                "downvotes": 0,
                "created_at": (now - timedelta(days=2)).isoformat(),
                "updated_at": (now - timedelta(days=2)).isoformat(),
            },
            "user-new": {
                "rating": 8,
                "review_text": "newer",
                "upvotes": 5,  # tie on upvotes
                "downvotes": 0,
                "created_at": (now - timedelta(hours=1)).isoformat(),  # more recent
                "updated_at": (now - timedelta(hours=1)).isoformat(),
            },
        }
        with open(reviews_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        movie_id = MovieRepository._slug(title)
        r = client.get(f"/reviews/{movie_id}?sort=upvotes")
        assert r.status_code == 200
        items = r.json()["items"]
        usernames = [item["user_id"] for item in items]
        # On tie by upvotes, secondary key is created_at (more recent first)
        assert usernames == ["user-new", "user-old"]
    finally:
        # cleanup
        if mdir.exists():
            for p in mdir.iterdir():
                p.unlink()
            mdir.rmdir()


def test_sort_recent_ties_follow_file_insertion_order():
    # When created_at timestamps are equal, sort by recent has no secondary key.
    # Because JSON preserves key order and Python dict preserves insertion order,
    # the listing should reflect the file's key order in a stable sort.
    title = "Test Sorting Ties Recent"
    mdir = Path(__file__).resolve().parents[2] / "backend" / "data" / "movies" / title
    mdir.mkdir(parents=True, exist_ok=True)
    try:
        reviews_path = mdir / "user_reviews.json"
        now = datetime.now(timezone.utc)
        same_ts = now.isoformat()
        data = {
            "user-a": {
                "rating": 6,
                "review_text": "A",
                "upvotes": 3,
                "downvotes": 0,
                "created_at": same_ts,
                "updated_at": same_ts,
            },
            "user-b": {
                "rating": 7,
                "review_text": "B",
                "upvotes": 9,
                "downvotes": 0,
                "created_at": same_ts,
                "updated_at": same_ts,
            },
        }
        with open(reviews_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        movie_id = MovieRepository._slug(title)
        r = client.get(f"/reviews/{movie_id}?sort=recent")
        assert r.status_code == 200
        items = r.json()["items"]
        usernames = [item["user_id"] for item in items]
        # With identical timestamps, order should match file insertion (user-a then user-b)
        assert usernames == ["user-a", "user-b"]
    finally:
        # cleanup
        if mdir.exists():
            for p in mdir.iterdir():
                p.unlink()
            mdir.rmdir()
