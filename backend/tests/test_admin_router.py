import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.security import create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    """
    Provide a fresh in-memory users store for each test by patching the user repository.
    """
    from backend.services.users_service import user_service  # shared instance

    store: list[dict] = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data  # mutate in place so references remain valid

    monkeypatch.setattr(user_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(user_service.user_repo, "save_users", fake_save)

    return store


def make_user(id: str, username: str, email: str, role: str = "user"):
    """
    Build a minimal user record suitable for admin tests.
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


def test_list_all_users_admin_only(clean_users):
    """
    Ensure only admins can list all users and non-admins receive a 403.
    """
    clean_users.extend(
        [
            make_user("1", "Alice", "a@x.com", role="user"),
            make_user("2", "Bob", "b@x.com", role="user"),
        ]
    )

    admin_token = create_access_token("admin123", "admin", 0)
    user_token = create_access_token("1", "user", 0)

    res = client.get("/admin/users", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

    res = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["username"] == "Alice"


def test_delete_user_as_admin(clean_users):
    """
    Admins can delete a user, removing them from the users store.
    """
    clean_users.append(make_user("1", "Target", "t@x.com"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.delete("/admin/users/1", headers={"Authorization": f"Bearer {admin_token}"})

    assert res.status_code in (200, 204)
    assert len(clean_users) == 0


def test_delete_user_forbidden_for_non_admin(clean_users):
    """
    Non-admin users are forbidden from deleting other users.
    """
    clean_users.append(make_user("1", "Target", "t@x.com"))
    user_token = create_access_token("1", "user", 0)

    res = client.delete("/admin/users/1", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403
    assert len(clean_users) == 1


def test_promote_user_success(clean_users):
    """
    Admins can promote a normal user to the admin role.
    """
    clean_users.append(make_user("1", "NormalUser", "n@x.com", role="user"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.post(
        "/admin/users/1/promote",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "admin"
    assert "promoted" in data["message"].lower()


def test_promote_user_already_admin(clean_users):
    """
    Promoting an already-admin user returns a 400 error.
    """
    clean_users.append(make_user("1", "AdminUser", "a@x.com", role="admin"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.post(
        "/admin/users/1/promote",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 400
    assert "already" in res.json()["detail"].lower()


def test_search_users_by_username(clean_users):
    """
    Admin search by username should match users case-insensitively.
    """
    clean_users.append(make_user("1", "Alice", "a@x.com", role="user"))
    clean_users.append(make_user("2", "Bob", "b@x.com", role="admin"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.get(
        "/admin/users/search",
        params={"username": "bob"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    usernames = {u["username"] for u in data}
    assert usernames == {"Bob"}


def test_search_no_results(clean_users):
    """
    Search with no matching users should return an empty list.
    """
    clean_users.append(make_user("1", "Alice", "a@x.com", role="user"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.get(
        "/admin/users/search",
        params={"username": "zzzzzz"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    assert res.json() == []


def test_search_users_by_email_partial_match(clean_users):
    """
    Admin search should support partial matches on email.
    """
    clean_users.append(make_user("1", "Alice", "a@x.com", role="user"))
    clean_users.append(make_user("2", "Bob", "b@x.com", role="admin"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.get(
        "/admin/users/search",
        params={"email": "@x"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    data = res.json()
    emails = {u["email"] for u in data}
    assert emails == {"a@x.com", "b@x.com"}


def test_search_users_by_email_and_role(clean_users):
    """
    Admin search should allow combining email and role filters.
    """
    clean_users.append(make_user("1", "User", "u@x.com", role="user"))
    clean_users.append(make_user("2", "Mod", "m@x.com", role="admin"))
    admin_token = create_access_token("a1", "admin", 0)

    res = client.get(
        "/admin/users/search",
        params={"email": "u@x.com", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    assert any("u@x.com" in u["email"] for u in res.json())


def test_admin_can_get_user_reviews(monkeypatch):
    """
    Admins can fetch all reviews for a given user via the admin endpoint.
    """
    admin_token = create_access_token("admin1", "admin", 0)

    fake_reviews = [
        {"movie_id": "m1", "rating": 8, "review_text": "Great"},
        {"movie_id": "m2", "rating": 9, "review_text": "Amazing"},
    ]

    def fake_get_user_reviews(uid):
        assert uid == "u1"
        return fake_reviews

    from backend.services.users_service import user_service
    monkeypatch.setattr(user_service, "get_user_reviews", fake_get_user_reviews)

    res = client.get(
        "/admin/users/u1/reviews",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    assert res.json() == fake_reviews


def test_non_admin_cannot_get_user_reviews():
    """
    Non-admin users are forbidden from listing another user's reviews.
    """
    token = create_access_token("u1", "user", 0)

    res = client.get(
        "/admin/users/u1/reviews",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403


def test_admin_can_delete_user_review(monkeypatch):
    """
    Admins can delete a specific review for a user via the admin endpoint.
    """
    admin_token = create_access_token("adm", "admin", 0)

    called: dict = {}

    def fake_delete(uid, movie_id):
        called["uid"] = uid
        called["movie_id"] = movie_id
        return {"status": "deleted"}

    from backend.services.users_service import user_service
    monkeypatch.setattr(user_service, "remove_review_from_user", fake_delete)

    res = client.delete(
        "/admin/users/u1/reviews/delete",
        params={"movie_id": "m2"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200
    assert res.json() == {"status": "deleted"}
    assert called == {"uid": "u1", "movie_id": "m2"}


def test_non_admin_cannot_delete_user_review():
    """
    Non-admin users are forbidden from deleting another user's review.
    """
    token = create_access_token("u1", "user", 0)

    res = client.delete(
        "/admin/users/u1/reviews/delete",
        params={"movie_id": "m2"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403
