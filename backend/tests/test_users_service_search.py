import pytest
from backend.services.users_service import user_service as users_service
from backend.schemas.user import UserCreate


@pytest.fixture
def memory_store(monkeypatch):
    """
    Provide a shared in-memory users store patched into the UserService repository.
    """
    store = []

    def fake_load_users():
        return store

    def fake_save_users(data):
        store[:] = data

    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)
    return store


@pytest.fixture
def sample_users(memory_store):
    """
    Seed the in-memory store with a small set of users for pure search tests.
    """
    memory_store[:] = [
        {"id": "1", "username": "Alice", "email": "a@x.com", "role": "admin"},
        {"id": "2", "username": "Bob", "email": "b@x.com", "role": "user"},
        {"id": "3", "username": "Charlie", "email": "c@x.org", "role": "user"},
    ]
    return memory_store


def test_search_by_username_exact(sample_users):
    """
    search_users should return a single exact match when username matches exactly.
    """
    results = users_service.search_users(username="Bob")
    assert len(results) == 1
    assert results[0]["username"] == "Bob"


def test_search_by_username_case_insensitive(sample_users):
    """
    search_users should perform case-insensitive matching on username.
    """
    results = users_service.search_users(username="bob")
    assert len(results) == 1
    assert results[0]["username"] == "Bob"


def test_search_empty_db(monkeypatch):
    """
    When the user store is empty, search_users should return an empty list.
    """
    monkeypatch.setattr(users_service.user_repo, "load_users", lambda: [])
    results = users_service.search_users(username="bob")
    assert results == []


def test_register_then_search_single_user(memory_store):
    """
    Registering a user should make them discoverable via search_users.
    """
    payload = UserCreate(username="Dora", email="d@x.com", password="pw")
    res = users_service.register(payload)
    assert isinstance(res, dict)
    assert "token" in res
    assert isinstance(res["token"], str)

    results = users_service.search_users(username="Dora")
    assert len(results) == 1
    assert results[0]["username"] == "Dora"


def test_register_multiple_and_search_case_insensitive(memory_store):
    """
    After registering multiple users, search_users should still match by username case-insensitively.
    """
    users_service.register(UserCreate(username="Eve", email="e@x.com", password="pw"))
    users_service.register(UserCreate(username="Frank", email="f@x.com", password="pw"))
    users_service.register(UserCreate(username="Grace", email="g@x.com", password="pw"))

    results = users_service.search_users(username="frank")
    assert len(results) == 1
    assert results[0]["username"] == "Frank"


def test_search_after_updates(memory_store):
    """
    Updating a user's username and email should be reflected in subsequent searches.
    """
    payload = UserCreate(username="Henry", email="h@x.com", password="pw")
    users_service.register(payload)
    user_id = memory_store[0]["id"]

    users_service.update_user(
        user_id,
        payload.__class__(username="Hank", email="hank@x.com", password="pw"),
    )

    results = users_service.search_users(username="Hank")
    assert len(results) == 1
    assert results[0]["username"] == "Hank"

    results_old = users_service.search_users(username="Henry")
    assert results_old == []
