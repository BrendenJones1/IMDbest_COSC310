import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import watchlist_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def watchlist_file(tmp_path, monkeypatch):
    """Isolate watchlist data per test run."""
    temp_file = tmp_path / "watchlist.json"
    temp_file.write_text(json.dumps({"users": []}), encoding="utf-8")
    monkeypatch.setattr(watchlist_service, "WATCHLIST_FILE", temp_file)
    monkeypatch.setattr(
        "backend.services.watchlist_service.WATCHLIST_FILE",
        temp_file,
        raising=False,
    )
    yield


def test_get_watchlist_unknown_user_returns_empty():
    resp = client.get("/watchlists/nonexistent")
    assert resp.status_code == 200
    body = resp.json()
    assert body["userId"] == "nonexistent"
    assert body["watchlist"] == []


def test_add_movie_creates_user_and_persists():
    resp = client.post(
        "/watchlists/u42/movies",
        json={"movieTitle": "Inception"},
    )
    assert resp.status_code == 201
    assert resp.json()["message"] == "New user added with first movie"

    get_resp = client.get("/watchlists/u42")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["userId"] == "u42"
    assert len(data["watchlist"]) == 1
    item = data["watchlist"][0]
    assert item["movieTitle"] == "Inception"
    assert "addedAt" in item


def test_add_duplicate_movie_returns_conflict():
    client.post(
        "/watchlists/u10/movies",
        json={"movieTitle": "Dune"},
    )
    resp = client.post(
        "/watchlists/u10/movies",
        json={"movieTitle": "Dune"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Movie already in watchlist"


def test_remove_existing_movie():
    client.post(
        "/watchlists/u7/movies",
        json={"movieTitle": "Arrival"},
    )

    resp = client.delete("/watchlists/u7/movies/Arrival")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Movie removed"

    remaining = client.get("/watchlists/u7").json()["watchlist"]
    assert remaining == []


def test_remove_unknown_user_returns_404():
    resp = client.delete("/watchlists/no_user/movies/Anything")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"


def test_remove_unknown_movie_returns_404():
    # Create user with one movie
    client.post("/watchlists/u11", json={"movieTitle": "Tenet"})

    # Try removing a different movie
    resp = client.delete("/watchlists/u11/NonexistentMovie")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Movie not found"
