import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.security import create_access_token

client = TestClient(app)

# -----------------------------
# Fixture: In-memory users.json
# -----------------------------
@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    from backend.services.users_service import user_service  # shared instance

    store: list[dict] = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data

    monkeypatch.setattr(user_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(user_service.user_repo, "save_users", fake_save)

    return store

# -----------------------------
# Fixture: isolated penalties JSON
# -----------------------------
@pytest.fixture(autouse=True)
def clean_penalties(monkeypatch, tmp_path):
    fake_penalty_file = tmp_path / "penalties.json"
    fake_penalty_file.write_text("[]")

    from backend.services.penalties_service import PenaltiesService
    from backend.services.users_service import user_service

    user_service.penalty_service = PenaltiesService(path=str(fake_penalty_file))

    return user_service.penalty_service

# -----------------------------
# Helper: make a user
# -----------------------------
def make_user(id, username, role):
    return {
        "id": id,
        "username": username,
        "email": username + "@x.com",
        "password_hash": "x",
        "role": role,
        "penalties": [],
        "reviews": [],
        "watchlist": []
    }


# ============================================================
# TEST: Non-admin forbidden
# ============================================================
def test_penalties_admin_required(clean_users):
    clean_users.append(make_user("u1", "UserOne", "user"))

    user_token = create_access_token("u1", "user")

    res = client.get(
        "/admin/users/u1/penalties",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert res.status_code == 403


# ============================================================
# TEST: Admin can view penalties
# ============================================================
def test_admin_can_get_penalties(clean_users):
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    res = client.get(
        "/admin/users/u1/penalties",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    assert res.json() == []


# ============================================================
# TEST: Admin can issue a penalty
# ============================================================
def test_admin_issue_penalty(clean_users):
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    res = client.post(
        "/admin/users/u1/penalties",
        params={"reason": "TestPenalty"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    penalty = res.json()
    assert penalty["reason"] == "TestPenalty"

    # User updated
    assert len(clean_users[0]["penalties"]) == 1


# ============================================================
# TEST: Admin can deactivate penalty
# ============================================================
def test_admin_deactivate_penalty(clean_users):
    clean_users.append(make_user("u1", "Bob", "user"))

    admin_token = create_access_token("admin1", "admin")

    # Issue a penalty
    issue = client.post(
        "/admin/users/u1/penalties",
        params={"reason": "Spam"},
        headers={"Authorization": f"Bearer {admin_token}"}
    ).json()

    p_id = issue["penalty_id"]

    # Deactivate it
    res = client.put(
        f"/admin/penalties/{p_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    assert res.json()["active"] is False
