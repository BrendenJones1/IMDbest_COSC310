# backend/tests/test_watchlist_integration.py

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import watchlist_service as wl

client = TestClient(app)

@pytest.fixture(autouse=True)
def temp_watchlist_file(monkeypatch) -> Path:
    """
    For each test, redirect wl.WATCHLIST_FILE to a temporary JSON file
    so that API tests do not affect backend/data/watchlist.json.
    """
    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp_dir.name) / "watchlist.json"

    monkeypatch.setattr(wl, "_tmp_dir_api", tmp_dir, raising=False)
    monkeypatch.setattr(wl, "WATCHLIST_FILE", tmp_path)

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"users": []}, f)

    return tmp_path

def test_post_creates_new_user_and_first_movie():
    """
    Case: user does not exist; API should create user and add first movie.
    We only assert status code and that the message is non-empty.
    """
    response = client.post(
        "/watchlists/u1/movies",
        json={"movieTitle": "Inception"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "message" in body
    assert isinstance(body["message"], str)
    assert body["message"] != ""

    # Verify via GET that Inception is present
    get_resp = client.get("/watchlists/u1")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["userId"] == "u1"
    titles = {m["movieTitle"] for m in data["watchlist"]}
    assert "Inception" in titles

def test_post_adds_second_movie_for_existing_user():
    """
    Case: user already exists; adding a new distinct movie.
    We assert status code and that both movies are present,
    ignoring any extra demo data (e.g., "m1").
    """
    client.post("/watchlists/u1/movies", json={"movieTitle": "Inception"})
    response = client.post("/watchlists/u1/movies", json={"movieTitle": "Dune"})

    assert response.status_code == 201
    body = response.json()
    assert "message" in body

    get_resp = client.get("/watchlists/u1")
    titles = {m["movieTitle"] for m in get_resp.json()["watchlist"]}
    assert "Inception" in titles
    assert "Dune" in titles


def test_post_prevents_duplicate_movie_with_409():
    """
    Case: duplicate movie for same user.
    Router turns the service message into HTTP 409 with detail.
    """
    client.post("/watchlists/u1/movies", json={"movieTitle": "Inception"})
    response = client.post("/watchlists/u1/movies", json={"movieTitle": "Inception"})

    assert response.status_code == 409
    body = response.json()
    assert body["detail"] == "Movie already in watchlist"


def test_post_invalid_body_missing_movie_title():
    """
    Case: request body is invalid (missing required field).
    FastAPI should return 422 Unprocessable Entity.
    """
    response = client.post("/watchlists/u1/movies", json={})
    assert response.status_code == 422


def test_get_watchlist_for_existing_user():
    """
    Case: user exists and has watchlist entries.
    We assert that both movies we add are present,
    but we do not require them to be the only movies.
    """
    client.post("/watchlists/u1/movies", json={"movieTitle": "Inception"})
    client.post("/watchlists/u1/movies", json={"movieTitle": "Dune"})

    resp = client.get("/watchlists/u1")
    assert resp.status_code == 200
    data = resp.json()

    assert data["userId"] == "u1"
    titles = {m["movieTitle"] for m in data["watchlist"]}
    assert "Inception" in titles
    assert "Dune" in titles


def test_get_watchlist_for_unknown_user_returns_empty_list():
    """
    Case: user does not exist.
    Router should return an empty watchlist (not an error).
    """
    resp = client.get("/watchlists/unknown")
    assert resp.status_code == 200
    data = resp.json()

    assert data["userId"] == "unknown"
    assert isinstance(data["watchlist"], list)
    assert data["watchlist"] == []


def test_delete_removes_movie():
    """
    Case: user exists and movie exists; should remove it.
    We assert that the movie we delete is no longer in the list,
    without assuming the list becomes completely empty.
    """
    client.post("/watchlists/u1/movies", json={"movieTitle": "Inception"})

    del_resp = client.delete("/watchlists/u1/movies/Inception")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"message": "Movie removed"}

    get_resp = client.get("/watchlists/u1")
    assert get_resp.status_code == 200
    titles = {m["movieTitle"] for m in get_resp.json()["watchlist"]}
    assert "Inception" not in titles


def test_delete_movie_not_found_still_200():
    """
    Case: user exists but the movie is not in the watchlist.
    Service returns "Movie not found", and router keeps status 200.
    We assert that the known existing movie is still there.
    """
    client.post("/watchlists/u1/movies", json={"movieTitle": "Dune"})

    del_resp = client.delete("/watchlists/u1/movies/Inception")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"message": "Movie not found"}

    get_resp = client.get("/watchlists/u1")
    titles = [m["movieTitle"] for m in get_resp.json()["watchlist"]]
    assert "Dune" in titles


def test_delete_user_not_found_returns_404():
    """
    Case: user does not exist.
    Router raises HTTP 404 with detail "User not found".
    """
    del_resp = client.delete("/watchlists/u999/movies/Inception")
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == "User not found"
