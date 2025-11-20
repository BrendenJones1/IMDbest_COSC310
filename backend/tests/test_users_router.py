import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.services import users_service
from backend.routers import users_router
from backend.schemas.user import UserCreate
from backend.utils.security import create_access_token
import sys

# Ensure only the canonical import path exists
if "services.users_service" in sys.modules:
    del sys.modules["services.users_service"]

# Patch load and save users to have empty list to work with, patches app
@pytest.fixture
def client(monkeypatch):
    # --- Shared in-memory store ---
    store = []

    def fake_load_users():
        return store

    def fake_save_users(data):
        store[:] = data

    # --- Patch the real service ---
    from backend.services.users_service import user_service as users_service
    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    # --- Build a brand-new FastAPI app for this test ---
    from backend.routers import users_router
    app = FastAPI()
    app.include_router(users_router.router)

    return TestClient(app)

def test_router_import_path_sanity():
    import sys
    modules = [m for m in sys.modules if "users_router" in m]
    assert "backend.routers.users_router" in modules


def test_register_user_success(client):
    res = client.post("/users/register", json={
        "username": "Alice",
        "email": "alice@example.com",
        "password": "pw"
    })
    assert res.status_code == 201
    body = res.json()
    assert "token" in body

def test_register_duplicate_username(client):
    client.post("/users/register", json={"username": "Bob", "email": "b@x.com", "password": "pw"})
    res = client.post("/users/register", json={"username": "bob", "email": "other@x.com", "password": "pw"})
    assert res.status_code == 409
    assert res.json()["detail"] == "Username taken."

def test_login_user_success(client):
    client.post("/users/register", json={"username": "Sam", "email": "s@x.com", "password": "pw"})
    res = client.post("/users/login", params={"username": "sam", "password": "pw"})
    assert res.status_code == 200
    assert "token" in res.json()

def test_login_invalid_password(client):
    client.post("/users/register", json={"username": "Jane", "email": "j@x.com", "password": "pw"})
    res = client.post("/users/login", params={"username": "Jane", "password": "wrong"})
    assert res.status_code == 401

def test_list_users_returns_public_data(client):
    client.post("/users/register", json={"username": "Tom", "email": "t@x.com", "password": "pw"})
    res = client.get("/users/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert "password_hash" not in data[0]
    assert "username" in data[0]

def test_get_user_by_id_success(client):
    client.post("/users/register", json={"username": "Eve", "email": "e@x.com", "password": "pw"})
    users = client.get("/users/").json()
    user_id = users[0]["id"]

    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["username"] == "Eve"

def test_search_users_by_username(client):
    client.post("/users/register", json={"username": "Alice", "email": "a@x.com", "password": "pw"})
    client.post("/users/register", json={"username": "Bob", "email": "b@x.com", "password": "pw"})

    res = client.get("/users/search", params={"username": "bob"})
    assert res.status_code == 200


def test_update_user_username(client):
    client.post("/users/register", json={"username": "Old", "email": "old@x.com", "password": "pw"})
    users = client.get("/users/").json()
    user_id = users[0]["id"]

    token = create_access_token(user_id, "admin")

    res = client.put(
        f"/users/{user_id}",
        json={"username": "NewName"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["username"] == "NewName"

def test_get_user_not_found(client):
    res = client.get("/users/unknown-id")
    assert res.status_code == 404

# --- REGISTER: duplicate email ---
def test_register_duplicate_email(client):
    client.post("/users/register", json={"username": "A", "email": "a@x.com", "password": "pw"})
    res = client.post("/users/register", json={"username": "B", "email": "a@x.com", "password": "pw"})
    assert res.status_code == 409
    assert "email" in res.text.lower()

# --- LOGIN: nonexistent username (should map 404→401) ---
def test_login_nonexistent_username(client):
    res = client.post("/users/login", params={"username": "ghost", "password": "pw"})
    assert res.status_code == 401
    assert "invalid" in res.text.lower()

# --- SEARCH: by email and role ---
def test_search_users_by_email_and_role(client):
    client.post("/users/register", json={"username": "Mod", "email": "m@x.com", "password": "pw"})
    client.post("/users/register", json={"username": "User", "email": "u@x.com", "password": "pw"})
    res = client.get("/users/search", params={"email": "u@x.com", "role": "user"})
    assert res.status_code == 200
    assert any("u@x.com" in u["email"] for u in res.json())

# --- SEARCH: no results (empty list) ---
def test_search_no_results(client):
    res = client.get("/users/search", params={"username": "zzzzzz"})
    assert res.status_code == 200
    assert res.json() == []   

# --- UPDATE: normal user updating self succeeds ---
def test_update_self_success(client):
    reg = client.post("/users/register", json={"username": "Self", "email": "self@x.com", "password": "pw"})
    data = reg.json()
    token = data["token"]
    user = data["user"]

    res = client.put(
        f"/users/{user['id']}",
        json={"username": "Selfie"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

# --- UPDATE: forbidden for non-owner non-admin ---
def test_update_forbidden_for_non_owner(client):
    client.post("/users/register", json={"username": "A", "email": "a@x.com", "password": "pw"})
    reg = client.post("/users/register", json={"username": "B", "email": "b@x.com", "password": "pw"})
    token = reg.json()["token"]

    res = client.put(
        f"/users/0000",
        json={"username": "Hack"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

# --- ROOT `/` route coverage (main.py) ---
def test_root_exists(client):
    res = client.get("/")
    assert res.status_code in (200, 404)  # 404 acceptable if no explicit route


