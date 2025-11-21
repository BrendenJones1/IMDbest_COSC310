import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.security import create_access_token
from contextlib import contextmanager

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    """
    Provide an in-memory users store for each test by monkeypatching the user repository.
    """
    from backend.services.users_service import user_service  # shared instance

    store: list[dict] = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data  # keep shared list reference stable across tests

    monkeypatch.setattr(user_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(user_service.user_repo, "save_users", fake_save)

    return store


@pytest.fixture(autouse=True)
def clean_penalties(monkeypatch, tmp_path):
    """
    Isolate penalties storage to a temporary JSON file for each test run.
    """
    fake_penalty_file = tmp_path / "penalties.json"
    fake_penalty_file.write_text("[]")

    from backend.services.penalties_service import PenaltiesService
    from backend.services.users_service import user_service

    user_service.penalty_service = PenaltiesService(path=str(fake_penalty_file))
    return user_service.penalty_service


def make_user(id, username, role):
    """
    Build a minimal user record suitable for tests.
    """
    return {
        "id": id,
        "username": username,
        "email": username + "@x.com",
        "password_hash": "x",
        "role": role,
        "penalties": [],
        "reviews": [],
        "watchlist": [],
    }


def test_penalties_admin_required(clean_users):
    """
    Non-admin users must be forbidden from accessing the penalties endpoint.
    """
    clean_users.append(make_user("u1", "UserOne", "user"))

    user_token = create_access_token("u1", "user")

    res = client.get(
        "/admin/users/u1/penalties",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert res.status_code == 403


def test_admin_can_get_penalties(clean_users):
    """
    Admins can fetch penalties for a user and receive an empty list when none exist.
    """
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    res = client.get(
        "/admin/users/u1/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    assert res.json() == []


def test_admin_issue_penalty(clean_users):
    """
    Admins can issue a penalty and it is reflected in both the response and user record.
    """
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    res = client.post(
        "/admin/users/u1/penalties",
        params={"reason": "TestPenalty"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    penalty = res.json()
    assert penalty["reason"] == "TestPenalty"

    # Verify the in-memory user store was updated with the new penalty
    assert len(clean_users[0]["penalties"]) == 1


def test_admin_deactivate_penalty(clean_users):
    """
    Admins can deactivate an existing penalty, marking it as inactive.
    """
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    issue = client.post(
        "/admin/users/u1/penalties",
        params={"reason": "Spam"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    p_id = issue["penalty_id"]

    res = client.put(
        f"/admin/penalties/{p_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    assert res.json()["active"] is False
