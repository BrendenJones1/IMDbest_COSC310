import pytest
from fastapi import HTTPException
from backend.repositories import users_repo
from backend.services import users_service
from backend.schemas.user import UserCreate, UserUpdate
from backend.utils.security import verify_password

@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    """Ensure tests always start with a clean users list."""
    store = []

    def fake_load_users():
        # Return a *copy* to simulate real file reads
        return store.copy()

    def fake_save_users(data):
        store.clear()
        store.extend(data)

    monkeypatch.setattr(users_service, "load_users", fake_load_users)
    monkeypatch.setattr(users_service, "save_users", fake_save_users)

    return store

def test_register_success():
    token = users_service.register(UserCreate(
        username="Alice",
        email="alice@example.com",
        password="12345"
    ))
    assert token is not None


def test_register_duplicate_username():
    users_service.register(UserCreate(username="Ben", email="b@x.com", password="pw"))
    with pytest.raises(HTTPException) as exc:
        users_service.register(UserCreate(username="ben", email="other@x.com", password="pw"))
    assert exc.value.status_code == 409


def test_register_duplicate_email():
    users_service.register(UserCreate(username="Ben", email="b@x.com", password="pw"))
    with pytest.raises(HTTPException):
        users_service.register(UserCreate(username="Benny", email="B@X.com", password="pw"))


def test_login_success():
    users_service.register(UserCreate(username="Sam", email="s@x.com", password="pw"))
    token = users_service.login("sam", "pw")
    assert token is not None


def test_login_wrong_password():
    users_service.register(UserCreate(username="Sam", email="s@x.com", password="pw"))
    with pytest.raises(HTTPException):
        users_service.login("sam", "wrong")


def test_get_user_by_id():
    users_service.register(UserCreate(username="Tom", email="t@x.com", password="pw"))
    users = users_service.list_users()
    u = users_service.get_user_by_id(users[0].id)
    assert u.username == "Tom"


def test_update_user_username_and_email():
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    user_id = users[0].id

    updated = users_service.update_user(user_id, UserUpdate(
        username="Adam",
        email="adam@x.com"
    ))
    assert updated.username == "Adam"
    assert updated.email == "adam@x.com"


def test_update_user_duplicate_username():
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users_service.register(UserCreate(username="B", email="b@x.com", password="pw"))
    users = users_service.list_users()

    # Try to rename second user to first user’s username
    with pytest.raises(HTTPException):
        users_service.update_user(users[1].id, UserUpdate(username="A"))


def test_update_password_hashes_correctly():
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    user_id = users[0].id

    users_service.update_user(user_id, UserUpdate(password="newpw"))
    stored = users_service._internal_get_user("A")  # get raw record

    assert verify_password("newpw", stored["password_hash"])


def test_delete_user_success():
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    users_service.delete_user(users[0].id)

    with pytest.raises(HTTPException):
        users_service.get_user_by_id(users[0].id)
