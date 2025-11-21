# backend/tests/test_user_repository.py

import json
from pathlib import Path

import pytest
from contextlib import contextmanager

from backend.repositories.users_repo import UserRepository


def test_default_users_file_location():
    """
    The default constructor points to .../data/users.json
    relative to this module.
    """
    repo = UserRepository()
    assert repo.users_file.name == "users.json"
    assert repo.users_file.parent.name == "data"


def test_load_users_returns_empty_list_when_file_missing(tmp_path: Path):
    """
    If the users file does not exist, load_users should return [].
    """
    users_file = tmp_path / "users.json"
    repo = UserRepository(users_file=users_file)

    result = repo.load_users()

    assert result == []


def test_save_users_writes_json_and_loads_back(tmp_path: Path):
    """
    save_users should write the given list to disk as JSON,
    and load_users should read it back unchanged.
    """
    users_file = tmp_path / "users.json"
    repo = UserRepository(users_file=users_file)

    users = [
        {"id": "1", "username": "Alice", "email": "a@example.com"},
        {"id": "2", "username": "Bob", "email": "b@example.com"},
    ]

    # when
    repo.save_users(users)

    # then: file exists and contains the JSON
    assert users_file.exists()

    with users_file.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    assert raw == users

    # and load_users reads the same data back
    loaded = repo.load_users()
    assert loaded == users


def test_save_users_uses_tmp_file_and_renames(tmp_path: Path):
    """
    save_users should write to a .tmp file and then atomically replace
    the target file.
    """
    users_file = tmp_path / "users.json"
    repo = UserRepository(users_file=users_file)

    users = [{"id": "1", "username": "Alice"}]

    repo.save_users(users)

    # final file exists
    assert users_file.exists()

    # tmp file should NOT exist anymore after os.replace
    tmp = users_file.with_suffix(".tmp")
    assert not tmp.exists()

    # content is correct
    with users_file.open("r", encoding="utf-8") as f:
        assert json.load(f) == users
