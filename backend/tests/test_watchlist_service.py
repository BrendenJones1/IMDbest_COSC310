# backend/tests/test_watchlist_service.py

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List

import pytest

# Import the actual service module
from services import watchlist_service as wl


# Helper utilities for mocking the file system
def _setup_temp_watchlist_file(
    monkeypatch,
    initial_data: Dict[str, Any] | None = None,
) -> Path:
    """
    Create a temporary JSON file and redirect wl.WATCHLIST_FILE to it.
    This ensures tests do not affect the actual backend/data/watchlist.json file.
    """
    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp_dir.name) / "watchlist.json"

    # Keep temporary directory alive until test ends
    monkeypatch.setattr(wl, "_tmp_dir", tmp_dir, raising=False)

    if initial_data is not None:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

    monkeypatch.setattr(wl, "WATCHLIST_FILE", tmp_path)
    return tmp_path


def _read_watchlist_file(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# get_user_watchlist tests
def test_get_user_watchlist_empty_when_file_missing(monkeypatch):
    """
    Case: watchlist file does not exist, and user does not exist.
    Expected: return empty list.
    """
    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp_dir.name) / "watchlist.json"

    monkeypatch.setattr(wl, "_tmp_dir", tmp_dir, raising=False)
    monkeypatch.setattr(wl, "WATCHLIST_FILE", tmp_path)

    result = wl.get_user_watchlist("u-new")
    assert result == []


def test_get_user_watchlist_existing_user(monkeypatch):
    """
    Case: file exists and the user has a populated watchlist.
    """
    initial = {
        "users": [
            {
                "userId": "u1",
                "watchlist": [
                    {"movieTitle": "Inception", "addedAt": "2025-01-01T12:00:00+00:00"},
                    {"movieTitle": "Dune", "addedAt": "2025-01-02T09:30:00+00:00"},
                ],
            }
        ]
    }
    _setup_temp_watchlist_file(monkeypatch, initial)

    result = wl.get_user_watchlist("u1")
    assert len(result) == 2
    titles = {m["movieTitle"] for m in result}
    assert titles == {"Inception", "Dune"}


# add_to_watchlist tests
def test_add_to_watchlist_creates_new_user(monkeypatch):
    """
    Case: user does not exist; create new user and add first movie.
    """
    path = _setup_temp_watchlist_file(monkeypatch, {"users": []})

    res = wl.add_to_watchlist("u1", "Inception")
    assert res == {"message": "New user added with first movie"}

    data = _read_watchlist_file(path)
    assert data["users"][0]["userId"] == "u1"
    assert data["users"][0]["watchlist"][0]["movieTitle"] == "Inception"


def test_add_to_watchlist_existing_user(monkeypatch):
    """
    Case: user exists and movie is added to watchlist.
    """
    initial = {
        "users": [
            {
                "userId": "u1",
                "watchlist": [
                    {"movieTitle": "Inception", "addedAt": "2025-01-01T12:00:00+00:00"}
                ],
            }
        ]
    }
    path = _setup_temp_watchlist_file(monkeypatch, initial)

    res = wl.add_to_watchlist("u1", "Dune")
    assert res == {"message": "Movie added"}

    data = _read_watchlist_file(path)
    titles = {m["movieTitle"] for m in data["users"][0]["watchlist"]}
    assert titles == {"Inception", "Dune"}


def test_add_to_watchlist_prevents_duplicates(monkeypatch):
    """
    Case: user exists and tries to add a duplicate movie.
    """
    initial = {
        "users": [
            {
                "userId": "u1",
                "watchlist": [
                    {"movieTitle": "Inception", "addedAt": "2025-01-01T12:00:00+00:00"}
                ],
            }
        ]
    }
    path = _setup_temp_watchlist_file(monkeypatch, initial)

    res = wl.add_to_watchlist("u1", "Inception")
    assert res == {"message": "Movie already in watchlist"}

    data = _read_watchlist_file(path)
    assert len(data["users"][0]["watchlist"]) == 1


def test_add_to_watchlist_accepts_empty_title_current_behavior(monkeypatch):
    """
    Boundary case: empty movie title.
    Current service implementation accepts it, so test reflects actual behavior.
    """
    path = _setup_temp_watchlist_file(monkeypatch, {"users": []})

    res = wl.add_to_watchlist("u1", "")
    assert "message" in res

    data = _read_watchlist_file(path)
    assert data["users"][0]["watchlist"][0]["movieTitle"] == ""


# remove_from_watchlist tests
def test_remove_from_watchlist_removes_movie(monkeypatch):
    initial = {
        "users": [
            {
                "userId": "u1",
                "watchlist": [
                    {"movieTitle": "Inception", "addedAt": "2025-01-01T12:00:00+00:00"},
                    {"movieTitle": "Dune", "addedAt": "2025-01-02T09:30:00+00:00"},
                ],
            }
        ]
    }
    path = _setup_temp_watchlist_file(monkeypatch, initial)

    res = wl.remove_from_watchlist("u1", "Inception")
    assert res == {"message": "Movie removed"}

    data = _read_watchlist_file(path)
    titles = {m["movieTitle"] for m in data["users"][0]["watchlist"]}
    assert titles == {"Dune"}


def test_remove_from_watchlist_movie_not_found(monkeypatch):
    initial = {
        "users": [
            {
                "userId": "u1",
                "watchlist": [
                    {"movieTitle": "Dune", "addedAt": "2025-01-02T09:30:00+00:00"},
                ],
            }
        ]
    }
    path = _setup_temp_watchlist_file(monkeypatch, initial)

    res = wl.remove_from_watchlist("u1", "Inception")
    assert res == {"message": "Movie not found"}


def test_remove_from_watchlist_user_not_found(monkeypatch):
    initial = {"users": [{"userId": "u2", "watchlist": []}]}
    _setup_temp_watchlist_file(monkeypatch, initial)

    res = wl.remove_from_watchlist("u1", "Inception")
    assert res == {"message": "User not found"}


# Fault injection + exception handling

def test_add_to_watchlist_raises_if_save_fails(monkeypatch):
    """
    Fault injection:
    Replace save_watchlists with a failing function and verify exception propagation.
    """
    _setup_temp_watchlist_file(monkeypatch, {"users": []})

    def fake_save(data):
        raise IOError("disk full")

    monkeypatch.setattr(wl, "save_watchlists", fake_save)

    with pytest.raises(IOError):
        wl.add_to_watchlist("u1", "Inception")
