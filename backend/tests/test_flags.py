import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.security import create_access_token
from backend.services import users_service
from backend.services.flags_service import FlagsService
from backend.services.users_service import user_service as users_service
from backend.routers.admin_router import router as admin_router
from contextlib import contextmanager


client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_flags_file(tmp_path, monkeypatch):
    """
    Use a temporary flags.json file for each test and wire it into the services.
    """
    fake_file = tmp_path / "flags.json"
    fake_file.write_text("[]")  # start with an empty flag store

    service = FlagsService(path=str(fake_file))

    # Patch the instance inside the shared UserService
    monkeypatch.setattr(users_service, "flags_service", service)

    # Patch the instance referenced by the admin router
    from backend.routers import admin_router
    monkeypatch.setattr(admin_router, "flags_service", service)

    return service


@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    """
    Provide an in-memory user store for each test by patching the user repository.
    """
    store: list[dict] = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data

    # Patch the repository methods used by UserService
    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save)

    return store


def make_user(id: str, username: str, email: str, role: str = "user"):
    """
    Build a minimal user record suitable for flag-related tests.
    """
    return {
        "id": id,
        "username": username,
        "email": email,
        "password_hash": "x",
        "role": role,
        "penalties": [],
        "reviews": [],
        "watchlist": [],
    }


def test_users_service_get_user_flags(clean_users, mock_flags_file):
    """
    UserService.get_user_flags should return only flags targeting the specified user.
    """
    clean_users.append(make_user("u1", "Alice", "a@x.com"))
    clean_users.append(make_user("u2", "Bob", "b@x.com"))

    mock_flags_file.add_flag("r1", "mod1", "u1", "Bad behavior")
    mock_flags_file.add_flag("r2", "mod2", "u1", "Spam")
    mock_flags_file.add_flag("r3", "mod3", "u2", "Rude")

    flags = users_service.get_user_flags("u1")

    assert len(flags) == 2
    assert all(f["flagged_user_id"] == "u1" for f in flags)


def test_users_service_change_flag_status(clean_users, mock_flags_file):
    """
    UserService.change_flag_status should delegate status updates to the flag service.
    """
    clean_users.append(make_user("u1", "Alice", "a@x.com"))

    flag = mock_flags_file.add_flag("r1", "admin", "u1", "Test flag")

    updated = users_service.change_flag_status(flag["flag_id"], "approved")

    assert updated["status"] == "approved"


def test_admin_get_all_flags(clean_users, mock_flags_file):
    """
    Admin endpoint /admin/flags should return all flags for an admin user.
    """
    clean_users.append(make_user("admin", "A", "admin@x.com", role="admin"))

    mock_flags_file.add_flag("r1", "u9", "u1", "Rule violation")
    mock_flags_file.add_flag("r2", "u9", "u2", "Spam")

    token = create_access_token("admin", "admin")

    res = client.get(
        "/admin/flags",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    assert len(res.json()) == 2


def test_admin_get_pending_flags(clean_users, mock_flags_file):
    """
    Admin endpoint /admin/flags/pending should include only flags still marked pending.
    """
    clean_users.append(make_user("admin", "A", "admin@x.com", role="admin"))

    f1 = mock_flags_file.add_flag("r1", "u9", "u1", "Rule violation")
    f2 = mock_flags_file.add_flag("r2", "u9", "u2", "Spam")
    mock_flags_file.update_flag_status(f2["flag_id"], "approved")

    token = create_access_token("admin", "admin")

    res = client.get(
        "/admin/flags/pending",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    returned = res.json()
    assert len(returned) == 1
    assert returned[0]["status"] == "pending"


def test_admin_update_flag_status(clean_users, mock_flags_file):
    """
    Admins can update a flag's status via /admin/flags/{flag_id}/status.
    """
    clean_users.append(make_user("admin", "A", "admin@x.com", role="admin"))

    flag = mock_flags_file.add_flag("r1", "mod9", "u1", "Bad behavior")

    token = create_access_token("admin", "admin")

    res = client.put(
        f"/admin/flags/{flag['flag_id']}/status",
        params={"new_status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    assert res.json()["status"] == "approved"


def test_admin_rejects_non_admin_access(clean_users, mock_flags_file):
    """
    Non-admin users should be forbidden from accessing /admin/flags.
    """
    clean_users.append(make_user("u1", "Normal", "n@x.com", role="user"))

    mock_flags_file.add_flag("r1", "u1", "u1", "Test issue")

    token = create_access_token("u1", "user")  # not an admin

    res = client.get(
        "/admin/flags",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403
