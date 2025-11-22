import pytest
from fastapi import HTTPException
from backend.services.users_service import user_service as users_service
from backend.schemas.user import UserCreate, UserUpdate
from backend.utils.security import verify_password
from datetime import datetime, timezone


@pytest.fixture(autouse=True)
def clean_users(monkeypatch):
    """
    Start each test with a clean in-memory users list patched into the repository.
    """
    store = []

    def fake_load_users():
        # Return a copy to mimic file reads and avoid accidental mutation
        return store.copy()

    def fake_save_users(data):
        store.clear()
        store.extend(data)

    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    return store


def test_register_sets_registered_at_field(clean_users):
    """
    Registering a user should set registered_at as a datetime within the call window and persist it.
    """
    before = datetime.utcnow()
    result = users_service.register(
        UserCreate(
            username="alice",
            email="alice@example.com",
            password="Secret123!",
        )
    )
    after = datetime.now(timezone.utc)

    user_public = result["user"]

    assert hasattr(user_public, "registered_at"), "registered_at missing on UserPublic"
    assert isinstance(
        user_public.registered_at, datetime
    ), f"registered_at should be datetime, got {type(user_public.registered_at)}"
    assert (
        before <= user_public.registered_at <= after
    ), "registered_at is not within expected time window"

    users = users_service.list_users()
    assert len(users) == 1
    stored_user = users[0]
    assert hasattr(stored_user, "registered_at")
    assert isinstance(stored_user.registered_at, datetime)


class DummyUser:
    """
    Lightweight stand-in for a user object with a username and token_version.
    """

    def __init__(self, username: str, token_version: int = 0):
        self.username = username
        self.token_version = token_version


def test_save_user_updates_existing_user_token_version(clean_users):
    """
    save_user should update token_version of an existing user matched by normalized username.
    """
    store = clean_users

    existing = DummyUser(" Alice ", token_version=0)
    store.append(existing)

    payload = DummyUser("  alice  ", token_version=5)

    users_service.save_user(payload)

    assert existing.token_version == 5
    assert len(store) == 1  # no extra users added


def test_save_user_raises_for_unknown_user(clean_users):
    """
    When no matching user exists, save_user should raise ValueError.
    """
    payload = DummyUser("ghost", token_version=1)

    with pytest.raises(ValueError) as exc:
        users_service.save_user(payload)

    assert "User ghost not found" in str(exc.value)


def test_save_user_propagates_save_error(clean_users, monkeypatch):
    """
    If the underlying repository save fails, save_user should propagate the exception.
    """
    store = clean_users
    store.append(DummyUser("bob", token_version=1))

    def boom(data):
        raise IOError("disk full")

    monkeypatch.setattr(users_service.user_repo, "save_users", boom)

    payload = DummyUser("bob", token_version=2)

    with pytest.raises(IOError) as exc:
        users_service.save_user(payload)

    assert "disk full" in str(exc.value)


def test_register_success():
    """
    A basic registration should succeed and return a token payload.
    """
    token = users_service.register(
        UserCreate(
            username="Alice",
            email="alice@example.com",
            password="12345",
        )
    )
    assert token is not None


def test_register_duplicate_username():
    """
    Registering with a duplicate username (case-insensitive) should raise 409 HTTPException.
    """
    users_service.register(UserCreate(username="Ben", email="b@x.com", password="pw"))
    with pytest.raises(HTTPException) as exc:
        users_service.register(
            UserCreate(username="ben", email="other@x.com", password="pw")
        )
    assert exc.value.status_code == 409


def test_register_duplicate_email():
    """
    Registering with an email already in use (case-insensitive) should raise HTTPException.
    """
    users_service.register(UserCreate(username="Ben", email="b@x.com", password="pw"))
    with pytest.raises(HTTPException):
        users_service.register(
            UserCreate(username="Benny", email="B@X.com", password="pw")
        )


def test_login_success():
    """
    login should succeed with correct credentials and return a token payload.
    """
    users_service.register(UserCreate(username="Sam", email="s@x.com", password="pw"))
    token = users_service.login("sam", "pw")
    assert token is not None


def test_login_wrong_password():
    """
    login should raise HTTPException when the password is incorrect.
    """
    users_service.register(UserCreate(username="Sam", email="s@x.com", password="pw"))
    with pytest.raises(HTTPException):
        users_service.login("sam", "wrong")


def test_get_user_by_id():
    """
    get_user_by_id should return the correct user when the id exists.
    """
    users_service.register(UserCreate(username="Tom", email="t@x.com", password="pw"))
    users = users_service.list_users()
    u = users_service.get_user_by_id(users[0].id)
    assert u.username == "Tom"


def test_update_user_username_and_email():
    """
    update_user should allow changing username and email when they are unique.
    """
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    user_id = users[0].id

    updated = users_service.update_user(
        user_id,
        UserUpdate(
            username="Adam",
            email="adam@x.com",
        ),
    )
    assert updated.username == "Adam"
    assert updated.email == "adam@x.com"


def test_update_user_duplicate_username():
    """
    Updating a user to a username already in use should raise HTTPException.
    """
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users_service.register(UserCreate(username="B", email="b@x.com", password="pw"))
    users = users_service.list_users()

    with pytest.raises(HTTPException):
        users_service.update_user(users[1].id, UserUpdate(username="A"))


def test_update_password_hashes_correctly():
    """
    Updating password should store a hash that verifies with the new password.
    """
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    user_id = users[0].id

    users_service.update_user(user_id, UserUpdate(password="newpw"))
    stored = users_service._internal_get_user("A")  # raw record with password_hash

    assert verify_password("newpw", stored["password_hash"])


def test_delete_user_success():
    """
    delete_user should remove the user so that subsequent lookups by id fail.
    """
    users_service.register(UserCreate(username="A", email="a@x.com", password="pw"))
    users = users_service.list_users()
    users_service.delete_user(users[0].id)

    with pytest.raises(HTTPException):
        users_service.get_user_by_id(users[0].id)
