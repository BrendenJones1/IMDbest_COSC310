import pytest
from backend.services.users_service import user_service as users_service


@pytest.fixture
def clean_users(monkeypatch):
    """
    Provide an isolated in-memory users store by patching the UserService repository.
    """
    store = []

    def fake_load_users():
        return store.copy()

    def fake_save_users(data):
        store[:] = data

    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    return store


def make_user(id: str, username: str, email: str, role: str = "user"):
    """
    Build a minimal user record suitable for admin search tests.
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


def test_search_users_admin_exact_username(clean_users):
    """
    Admin search should return a single match when username matches exactly.
    """
    clean_users.extend([
        make_user("1", "Alice", "a@x.com"),
        make_user("2", "Bob", "b@x.com"),
    ])

    results = users_service.search_users_admin(username="Alice")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_case_insensitive(clean_users):
    """
    Admin search by username should be case-insensitive.
    """
    clean_users.extend([
        make_user("1", "Alice", "a@x.com"),
        make_user("2", "Bob", "b@x.com"),
    ])

    results = users_service.search_users_admin(username="alice")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_partial_email(clean_users):
    """
    Admin search should support partial email matches.
    """
    clean_users.extend([
        make_user("1", "Alice", "test@domain.com"),
        make_user("2", "Bob", "other@domain.com"),
    ])

    results = users_service.search_users_admin(email="domain")
    assert len(results) == 2
    assert {u["id"] for u in results} == {"1", "2"}


def test_search_users_admin_role_filter(clean_users):
    """
    Admin search should filter users by role when a role is provided.
    """
    clean_users.extend([
        make_user("1", "Alice", "a@x.com", role="user"),
        make_user("2", "Bob", "b@x.com", role="admin"),
        make_user("3", "Carl", "c@x.com", role="admin"),
    ])

    results = users_service.search_users_admin(role="admin")
    assert len(results) == 2
    assert {u["id"] for u in results} == {"2", "3"}


def test_search_users_admin_multiple_filters(clean_users):
    """
    Admin search should apply username and role filters together.
    """
    clean_users.extend([
        make_user("1", "Alice Wonderland", "alice@x.com", role="admin"),
        make_user("2", "Alice Smith", "asmith@x.com", role="user"),
        make_user("3", "Bob", "bob@x.com", role="admin"),
    ])

    results = users_service.search_users_admin(username="alice", role="admin")
    assert len(results) == 1
    assert results[0]["id"] == "1"


def test_search_users_admin_no_filters_returns_all(clean_users):
    """
    When no filters are provided, admin search should return all users.
    """
    clean_users.extend([
        make_user("1", "A", "a@x.com"),
        make_user("2", "B", "b@x.com"),
    ])

    results = users_service.search_users_admin()
    assert len(results) == 2
    assert {u["id"] for u in results} == {"1", "2"}
