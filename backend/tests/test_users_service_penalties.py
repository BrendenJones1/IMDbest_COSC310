import pytest
from backend.services.users_service import user_service
from backend.services.penalties_service import PenaltiesService
from contextlib import contextmanager


@pytest.fixture
def fake_penalty_store(tmp_path, monkeypatch):
    """
    Provide a PenaltiesService instance backed by a temporary penalties.json file,
    and wire it into the shared UserService instance.
    """
    fake_file = tmp_path / "penalties.json"
    fake_file.write_text("[]")

    service = PenaltiesService(path=str(fake_file))

    monkeypatch.setattr(user_service, "penalty_service", service)

    return service


@pytest.fixture
def fake_users(monkeypatch):
    """
    Provide an in-memory users store and patch the UserService repository to use it.
    """
    store: list[dict] = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data

    monkeypatch.setattr(user_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(user_service.user_repo, "save_users", fake_save)

    return store


def test_add_penalty_to_user(fake_users, fake_penalty_store):
    """
    add_penalty_to_user should create a penalty record and attach it to the user.
    """
    fake_users.append({
        "id": "u1",
        "username": "Bob",
        "penalties": [],
    })

    result = user_service.add_penalty_to_user(
        user_id="u1",
        reason="Spam",
        admin_id="a1",
        flag_id=None,
    )

    penalties = fake_penalty_store.get_all()
    assert len(penalties) == 1
    assert penalties[0]["reason"] == "Spam"

    assert len(fake_users[0]["penalties"]) == 1
    assert fake_users[0]["penalties"][0]["reason"] == "Spam"


def test_get_user_penalties(fake_users, fake_penalty_store):
    """
    get_user_penalties should return penalties associated with the given user.
    """
    fake_penalty_store.add_penalty("u1", "Bad behavior", "admin1")

    penalties = user_service.get_user_penalties("u1")
    assert len(penalties) == 1
    assert penalties[0]["reason"] == "Bad behavior"


def test_deactivate_penalty(fake_users, fake_penalty_store):
    """
    deactivate_penalty should mark the penalty inactive in both penalty storage and user records.
    """
    fake_users.append({"id": "u1", "penalties": []})
    p = fake_penalty_store.add_penalty("u1", "Abuse", "admin1")

    fake_users[0]["penalties"].append(p)

    updated = user_service.deactivate_penalty(
        penalty_id=p["penalty_id"],
        admin_id="adminX",
    )

    assert updated is not None
    assert updated["active"] is False

    assert fake_users[0]["penalties"][0]["active"] is False
