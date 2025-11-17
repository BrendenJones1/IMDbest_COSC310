import pytest
from backend.services.users_service import user_service as users_service


# -----------------------------------------------------
# Fixture: isolated in-memory users store
# -----------------------------------------------------
@pytest.fixture
def clean_users(monkeypatch):
    store = []

    def fake_load_users():
        return store.copy()

    def fake_save_users(data):
        store[:] = data

    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    return store


# -----------------------------------------------------
# Helper
# -----------------------------------------------------
def make_user(id: str, username: str, email: str, role: str = "user"):
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


# -----------------------------------------------------
# TESTS
# -----------------------------------------------------

def test_search_users_admin_exact_username(clean_users):
    clean_users.extend([
        make_user("1", "Alice", "a@x.com"),
        make_user("2", "Bob", "b@x.com"),
    ])

    results = users_service.search_users_admin(username="Alice")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_case_insensitive(clean_users):
    clean_users.extend([
        make_user("1", "Alice", "a@x.com"),
        make_user("2", "Bob", "b@x.com"),
    ])

    results = users_service.search_users_admin(username="alice")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_partial_email(clean_users):
    clean_users.extend([
        make_user("1", "Alice", "test@domain.com"),
        make_user("2", "Bob", "other@domain.com"),
    ])

    results = users_service.search_users_admin(email="domain")
    assert len(results) == 2
    assert {u["id"] for u in results} == {"1", "2"}


def test_search_users_admin_role_filter(clean_users):
    clean_users.extend([
        make_user("1", "Alice", "a@x.com", role="user"),
        make_user("2", "Bob", "b@x.com", role="admin"),
        make_user("3", "Carl", "c@x.com", role="admin"),
    ])

    results = users_service.search_users_admin(role="admin")
    assert len(results) == 2
    assert {u["id"] for u in results} == {"2", "3"}


def test_search_users_admin_multiple_filters(clean_users):
    clean_users.extend([
        make_user("1", "Alice Wonderland", "alice@x.com", role="admin"),
        make_user("2", "Alice Smith", "asmith@x.com", role="user"),
        make_user("3", "Bob", "bob@x.com", role="admin"),
    ])

    results = users_service.search_users_admin(username="alice", role="admin")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_no_filters_returns_all(clean_users):
    clean_users.extend([
        make_user("1", "A", "a@x.com"),
        make_user("2", "B", "b@x.com"),
    ])

    results = users_service.search_users_admin()
    assert len(results) == 2
    assert {u["id"] for u in results} == {"1", "2"}
