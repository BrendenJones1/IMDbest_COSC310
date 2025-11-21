import json
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import watchlist_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def watchlist_file(tmp_path, monkeypatch):
    """
    Use a temporary watchlist.json file so tests do not touch real data.
    """
    temp_file = tmp_path / "watchlist.json"
    temp_file.write_text(json.dumps({"users": []}), encoding="utf-8")
    monkeypatch.setattr(watchlist_service, "WATCHLIST_FILE", temp_file)
    monkeypatch.setattr("backend.services.watchlist_service.WATCHLIST_FILE", temp_file, raising=False)
    yield


def test_get_watchlist_unknown_user_returns_empty():
    """
    Getting the watchlist for an unknown user should return an empty list with 200 OK.
    """
    resp = client.get("/watchlists/nonexistent")
    assert resp.status_code == 200
    body = resp.json()
    assert body["userId"] == "nonexistent"
    assert body["watchlist"] == []


def test_add_movie_creates_user_and_persists():
    """
    Adding a movie for a new user should create the user and persist the watchlist entry.
    """
    resp = client.post("/watchlists/u42", json={"movieTitle": "Inception"})
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
    """
    Adding the same movie twice for a user should return a 409 conflict.
    """
    client.post("/watchlists/u10", json={"movieTitle": "Dune"})
    resp = client.post("/watchlists/u10", json={"movieTitle": "Dune"})
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Movie already in watchlist"


def test_remove_existing_movie():
    """
    Removing an existing movie should succeed and leave the user's watchlist empty.
    """
    client.post("/watchlists/u7", json={"movieTitle": "Arrival"})

    resp = client.delete("/watchlists/u7/Arrival")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Movie removed"

    remaining = client.get("/watchlists/u7").json()["watchlist"]
    assert remaining == []


def test_remove_unknown_user_returns_404():
    """
    Removing a movie for an unknown user should return 404 User not found.
    """
    resp = client.delete("/watchlists/no_user/Anything")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"


def test_remove_unknown_movie_returns_404():
    """
    Removing a movie that is not in the user's watchlist should return 404 Movie not found.
    """
    client.post("/watchlists/u11", json={"movieTitle": "Tenet"})

    resp = client.delete("/watchlists/u11/NonexistentMovie")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Movie not found"
