from pathlib import Path
import json
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers.reviews_router import router as reviews_router
from backend.repositories.movie_repo import MovieRepository

# use: pytest backend/tests/test_review_username.py -v
# to see test output
app = FastAPI()
app.include_router(reviews_router)
client = TestClient(app)


def _movie_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "backend" / "data" / "movies" / "Test Movie Username"


def setup_module(module=None):
    # Use existing user from backend/data/users.json
    user_id = "1d51a572-0365-46b3-a4f1-6cc588ca4f53"
    # Prepare a test movie with one review from that user
    mdir = _movie_dir()
    mdir.mkdir(parents=True, exist_ok=True)
    reviews_path = mdir / "user_reviews.json"
    now = datetime.now(timezone.utc).isoformat()
    review = {
        "rating": 8,
        "review_text": "solid film",
        "upvotes": 4,
        "downvotes": 0,
        "created_at": now,
        "updated_at": now,
    }
    with reviews_path.open("w", encoding="utf-8") as f:
        json.dump({user_id: review}, f, indent=2)


def teardown_module(module=None):
    mdir = _movie_dir()
    if mdir.exists():
        for p in mdir.iterdir():
            p.unlink()
        mdir.rmdir()


def test_review_payload_includes_username_and_fields():
    movie_id = MovieRepository._slug("Test Movie Username")
    r = client.get(f"/reviews/{movie_id}?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    item = data["items"][0]
    # username joined from users.json
    assert item["username"] == "A"
    # required fields present
    assert isinstance(item["upvotes"], int)
    assert isinstance(item["review_text"], str)
    # ISO-ish date strings from FastAPI serialization of datetime
    assert "T" in item["created_at"]
    assert "T" in item["updated_at"]

