from pathlib import Path
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers.movies_router import router as movies_router
from backend.repositories.movie_repo import MovieRepository

app = FastAPI()
app.include_router(movies_router)
client = TestClient(app)


def _movie_dir(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "backend" / "data" / "movies" / name


def setup_module(module=None):
    # Create two movies: one with metadata, one without
    with_meta = _movie_dir("Test Meta Present")
    with_meta.mkdir(parents=True, exist_ok=True)
    with open(with_meta / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "movie_id": MovieRepository._slug("Test Meta Present"),
                "title": "Test Meta Present",
                "userRatingAverage": 8.2,
                "userRatingCount": 12,
            },
            f,
            indent=2,
        )

    without_meta = _movie_dir("Test Meta Missing")
    without_meta.mkdir(parents=True, exist_ok=True)
    # Intentionally do not write metadata.json here


def teardown_module(module=None):
    for name in ["Test Meta Present", "Test Meta Missing"]:
        mdir = _movie_dir(name)
        if mdir.exists():
            for p in mdir.iterdir():
                p.unlink()
            mdir.rmdir()


def test_metadata_present_returns_values():
    movie_id = MovieRepository._slug("Test Meta Present")
    r = client.get(f"/movies/{movie_id}/metadata")
    assert r.status_code == 200
    data = r.json()
    assert data["movie_id"] == movie_id
    assert data["title"] == "Test Meta Present"
    assert data["userRatingAverage"] == 8.2
    assert data["userRatingCount"] == 12


def test_metadata_missing_returns_defaults():
    movie_id = MovieRepository._slug("Test Meta Missing")
    r = client.get(f"/movies/{movie_id}/metadata")
    assert r.status_code == 200
    data = r.json()
    assert data["movie_id"] == movie_id
    # Title may be None if not present; average and count should default
    assert data["userRatingAverage"] == 0.0
    assert data["userRatingCount"] == 0

