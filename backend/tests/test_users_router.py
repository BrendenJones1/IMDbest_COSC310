import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from backend.services.users_service import user_service as users_service
from backend.routers import users_router
from backend.schemas.user import UserCreate
from backend.utils.security import create_access_token
from datetime import datetime, timezone
import sys

# Ensure only the canonical import path exists
if "services.users_service" in sys.modules:
    del sys.modules["services.users_service"]


@pytest.fixture
def client(monkeypatch):
    """
    Build a fresh FastAPI app with a clean in-memory users store for each test.
    """
    store = []

    def fake_load_users():
        return store

    def fake_save_users(data):
        store[:] = data

    from backend.services.users_service import user_service as users_service
    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    from backend.routers import users_router
    app = FastAPI()
    app.include_router(users_router.router)

    return TestClient(app)


def test_register_response_has_registered_at(client):
    """
    /users/register should include a registered_at field with a valid ISO 8601 datetime.
    """
    resp = client.post(
        "/users/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "AnotherSecret123!",
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert "user" in body
    user = body["user"]

    assert "registered_at" in user, "registered_at missing from API response"
    assert user["registered_at"] is not None

    parsed = datetime.fromisoformat(user["registered_at"])
    assert isinstance(parsed, datetime)


class DummyUser:
    """
    Simple stand-in for a user object with a mutable token_version.
    """

    def __init__(self, username: str, token_version: int = 0):
        self.username = username
        self.token_version = token_version


def test_logout_increments_token_version_and_saves(client, monkeypatch):
    """
    Logout should increment token_version and persist the updated user via save_user.
    """
    app = client.app

    fake_user = DummyUser("alice", token_version=3)

    app.dependency_overrides[users_router.get_current_user] = lambda: fake_user

    saved_payloads = []

    def fake_save_user(payload):
        saved_payloads.append(payload)

    monkeypatch.setattr(users_service, "save_user", fake_save_user, raising=True)

    response = client.post("/users/logout")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert fake_user.token_version == 4
    assert len(saved_payloads) == 1
    assert saved_payloads[0] is fake_user
    assert saved_payloads[0].token_version == 4


def test_logout_propagates_save_failure(client, monkeypatch):
    """
    If save_user raises, the exception should propagate out of the logout request.
    """
    app = client.app

    fake_user = DummyUser("alice", token_version=1)
    app.dependency_overrides[users_router.get_current_user] = lambda: fake_user

    def boom(payload):
        raise RuntimeError("disk full")

    monkeypatch.setattr(users_service, "save_user", boom, raising=True)

    with pytest.raises(RuntimeError, match="disk full"):
        client.post("/users/logout")


def test_router_import_path_sanity():
    """
    Ensure the users_router module is imported via the canonical backend path.
    """
    import sys

    modules = [m for m in sys.modules if "users_router" in m]
    assert "backend.routers.users_router" in modules


def test_register_user_success(client):
    """
    Registering a new user should succeed and return an access token.
    """
    res = client.post(
        "/users/register",
        json={
            "username": "Alice",
            "email": "alice@example.com",
            "password": "pw",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert "token" in body


def test_register_duplicate_username(client):
    """
    Registering with an existing username (case-insensitive) should return 409.
    """
    client.post(
        "/users/register",
        json={"username": "Bob", "email": "b@x.com", "password": "pw"},
    )
    res = client.post(
        "/users/register",
        json={"username": "bob", "email": "other@x.com", "password": "pw"},
    )
    assert res.status_code == 409
    assert res.json()["detail"] == "Username taken."


def test_login_user_success(client):
    """
    Valid credentials should allow a user to obtain a token via /users/login.
    """
    client.post(
        "/users/register",
        json={"username": "Sam", "email": "s@x.com", "password": "pw"},
    )
    res = client.post(
        "/users/login",
        params={"username": "sam", "password": "pw"},
    )
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_invalid_password(client):
    """
    Incorrect password should yield a 401 Unauthorized response.
    """
    client.post(
        "/users/register",
        json={"username": "Jane", "email": "j@x.com", "password": "pw"},
    )
    res = client.post(
        "/users/login",
        params={"username": "Jane", "password": "wrong"},
    )
    assert res.status_code == 401


def test_list_users_returns_public_data(client):
    """
    Listing users should return public-safe data without password_hash.
    """
    client.post(
        "/users/register",
        json={"username": "Tom", "email": "t@x.com", "password": "pw"},
    )
    res = client.get("/users/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert "password_hash" not in data[0]
    assert "username" in data[0]


def test_get_user_by_id_success(client):
    """
    /users/{id} should return the requested user when the id exists.
    """
    client.post(
        "/users/register",
        json={"username": "Eve", "email": "e@x.com", "password": "pw"},
    )
    users = client.get("/users/").json()
    user_id = users[0]["id"]

    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["username"] == "Eve"


def test_search_users_by_username(client):
    """
    /users/search should support case-insensitive username searches.
    """
    client.post(
        "/users/register",
        json={"username": "Alice", "email": "a@x.com", "password": "pw"},
    )
    client.post(
        "/users/register",
        json={"username": "Bob", "email": "b@x.com", "password": "pw"},
    )

    res = client.get("/users/search", params={"username": "bob"})
    assert res.status_code == 200


def test_update_user_username(client):
    """
    Admin can update a user's username via /users/{user_id}.
    """
    client.post(
        "/users/register",
        json={"username": "Old", "email": "old@x.com", "password": "pw"},
    )
    users = client.get("/users/").json()
    user_id = users[0]["id"]

    token = create_access_token(user_id, "admin", 0)

    res = client.put(
        f"/users/{user_id}",
        json={"username": "NewName"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["username"] == "NewName"


def test_get_user_not_found(client):
    """
    Requesting a non-existent user id should return 404.
    """
    res = client.get("/users/unknown-id")
    assert res.status_code == 404


def test_register_duplicate_email(client):
    """
    Duplicate email registration attempts should result in a 409 conflict.
    """
    client.post(
        "/users/register",
        json={"username": "A", "email": "a@x.com", "password": "pw"},
    )
    res = client.post(
        "/users/register",
        json={"username": "B", "email": "a@x.com", "password": "pw"},
    )
    assert res.status_code == 409
    assert "email" in res.text.lower()


def test_login_nonexistent_username(client):
    """
    Logging in with a non-existent username should return 401 with a generic message.
    """
    res = client.post(
        "/users/login",
        params={"username": "ghost", "password": "pw"},
    )
    assert res.status_code == 401
    assert "incorrect" in res.text.lower()


def test_search_users_by_email_and_role(client):
    """
    /users/search should allow filtering by both email and role.
    """
    client.post(
        "/users/register",
        json={"username": "Mod", "email": "m@x.com", "password": "pw"},
    )
    client.post(
        "/users/register",
        json={"username": "User", "email": "u@x.com", "password": "pw"},
    )
    res = client.get(
        "/users/search",
        params={"email": "u@x.com", "role": "user"},
    )
    assert res.status_code == 200
    assert any("u@x.com" in u["email"] for u in res.json())


def test_search_no_results(client):
    """
    Searching with no matches should return an empty list and 200 OK.
    """
    res = client.get("/users/search", params={"username": "zzzzzz"})
    assert res.status_code == 200
    assert res.json() == []


def test_update_self_success(client):
    """
    A normal user should be able to update their own profile data.
    """
    reg = client.post(
        "/users/register",
        json={"username": "Self", "email": "self@x.com", "password": "pw"},
    )
    data = reg.json()
    token = data["token"]
    user = data["user"]

    res = client.put(
        f"/users/{user['id']}",
        json={"username": "Selfie"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200


def test_update_forbidden_for_non_owner(client):
    """
    Non-admin users should be forbidden from updating other users' profiles.
    """
    client.post(
        "/users/register", 
        json={"username": "A", "email": "a@x.com", "password": "pw"},
    )
    reg = client.post(
        "/users/register",
        json={"username": "B", "email": "b@x.com", "password": "pw"},
    )
    token = reg.json()["token"]

    res = client.put(
        "/users/0000",
        json={"username": "Hack"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


def test_root_exists(client):
    """
    Root route should exist or cleanly return 404 if not explicitly defined.
    """
    res = client.get("/")
    assert res.status_code in (200, 404)
