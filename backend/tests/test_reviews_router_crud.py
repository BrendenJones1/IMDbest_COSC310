import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories import movie_repo as movie_repo_module
from backend.repositories.movie_repo import MovieRepository

client = TestClient(app)


@pytest.fixture(autouse=True)
def movies_dir(tmp_path, monkeypatch):
    """
    Isolate the movies data directory for each test run.
    """
    base = tmp_path / "movies"
    base.mkdir()
    # Patch both namespaces defensively
    monkeypatch.setattr(movie_repo_module, "MOVIES_DIR", base, raising=False)
    monkeypatch.setattr("backend.repositories.movie_repo.MOVIES_DIR", base, raising=False)
    try:
        monkeypatch.setattr("repositories.movie_repo.MOVIES_DIR", base, raising=False)
    except Exception:
        pass
    return base


def _write_movie(movies_dir: Path, title: str, with_meta: bool = True) -> str:
    """
    Create a movie directory (and metadata.json optionally) and return slug id.
    """
    movie_dir = movies_dir / title
    movie_dir.mkdir(parents=True, exist_ok=True)
    if with_meta:
        (movie_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "title": title,
                    # optional fields used elsewhere; harmless if unused
                    "userRatingCount": 0,
                    "userRatingTotal": 0.0,
                    "userRatingAverage": 0.0,
                }
            ),
            encoding="utf-8",
        )
    return MovieRepository._slug(title)


def test_post_creates_then_get_returns_review(movies_dir: Path):
    movie_id = _write_movie(movies_dir, "API Review Movie")
    user_id = "user-xyz"
    payload = {"rating": 4.0, "review_text": "Nice"}

    r = client.post(f"/reviews/{movie_id}/{user_id}", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == user_id
    assert data["rating"] == 4.0
    assert data["review_text"] == "Nice"
    assert "created_at" in data and "updated_at" in data

    # GET should return the same review
    r = client.get(f"/reviews/{movie_id}/{user_id}")
    assert r.status_code == 200
    got = r.json()
    assert got["user_id"] == user_id
    assert got["rating"] == 4.0
    assert got["review_text"] == "Nice"


def test_post_updates_returns_200_and_changes_rating(movies_dir: Path):
    movie_id = _write_movie(movies_dir, "Update Review Movie")
    user_id = "user-a"

    r = client.post(f"/reviews/{movie_id}/{user_id}", json={"rating": 3.0})
    assert r.status_code == 201
    r = client.post(f"/reviews/{movie_id}/{user_id}", json={"rating": 5.0, "review_text": "Great"})
    assert r.status_code == 200
    data = r.json()
    assert data["rating"] == 5.0
    assert data["review_text"] == "Great"

    # Check list endpoint reflects one review
    r = client.get(f"/reviews/{movie_id}")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["rating"] == 5.0


def test_delete_review_returns_204_and_subsequent_get_404(movies_dir: Path):
    movie_id = _write_movie(movies_dir, "Delete Review Movie")
    user_id = "u-del"
    client.post(f"/reviews/{movie_id}/{user_id}", json={"rating": 4.5})

    r = client.delete(f"/reviews/{movie_id}/{user_id}")
    assert r.status_code == 204

    r = client.get(f"/reviews/{movie_id}/{user_id}")
    assert r.status_code == 404

    # list endpoint should be empty
    r = client.get(f"/reviews/{movie_id}")
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_get_user_review_404_when_missing(movies_dir: Path):
    movie_id = _write_movie(movies_dir, "No Review Yet")
    r = client.get(f"/reviews/{movie_id}/unknown-user")
    assert r.status_code == 404


def test_post_invalid_rating_422(movies_dir: Path):
    movie_id = _write_movie(movies_dir, "Bad Rating Movie")
    user_id = "u-bad"
    # rating out of bounds
    r = client.post(f"/reviews/{movie_id}/{user_id}", json={"rating": 10})
    assert r.status_code == 422


def test_post_404_when_movie_missing(movies_dir: Path):
    # no folder written for this slug
    missing_movie_id = MovieRepository._slug("Definitely Missing")
    r = client.post(f"/reviews/{missing_movie_id}/user-z", json={"rating": 4.0})
    assert r.status_code == 404


