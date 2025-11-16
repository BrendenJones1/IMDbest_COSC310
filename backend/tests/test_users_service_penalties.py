import pytest
from backend.services.users_service import user_service 
from backend.services.penalties_service import PenaltiesService


# --------------------------- 
# FIXTURE: Fake penalty store
# ---------------------------
@pytest.fixture
def fake_penalty_store(tmp_path, monkeypatch):
    """Provide an isolated penalties.json file."""
    fake_file = tmp_path / "penalties.json"
    fake_file.write_text("[]")

    service = PenaltiesService(path=str(fake_file))

    # Override the penalty_service instance inside user_service
    monkeypatch.setattr(user_service, "penalty_service", service)

    return service


# ---------------------------
# FIXTURE: Fake users store
# ---------------------------
@pytest.fixture
def fake_users(monkeypatch):
    store = []

    def fake_load():
        return store.copy()

    def fake_save(data):
        store[:] = data

    # Patch the repository used by UserService
    monkeypatch.setattr(user_service.user_repo, "load_users", fake_load)
    monkeypatch.setattr(user_service.user_repo, "save_users", fake_save)

    return store

# ==========================================================
# TEST add_penalty_to_user
# ==========================================================
def test_add_penalty_to_user(fake_users, fake_penalty_store):
    fake_users.append({
        "id": "u1",
        "username": "Bob",
        "penalties": []
    })

    result = user_service.add_penalty_to_user(
        user_id="u1",
        reason="Spam",
        admin_id="a1",
        flag_id=None
    )

    # Penalty file updated
    penalties = fake_penalty_store.get_all()
    assert len(penalties) == 1
    assert penalties[0]["reason"] == "Spam"

    # User updated
    assert len(fake_users[0]["penalties"]) == 1
    assert fake_users[0]["penalties"][0]["reason"] == "Spam"


# ==========================================================
# TEST get_user_penalties
# ==========================================================
def test_get_user_penalties(fake_users, fake_penalty_store):
    # Create a penalty for u1
    fake_penalty_store.add_penalty("u1", "Bad behavior", "admin1")

    penalties = user_service.get_user_penalties("u1")
    assert len(penalties) == 1
    assert penalties[0]["reason"] == "Bad behavior"


# ==========================================================
# TEST deactivate_penalty
# ==========================================================
def test_deactivate_penalty(fake_users, fake_penalty_store):
    # Setup user record + penalty file
    fake_users.append({"id": "u1", "penalties": []})
    p = fake_penalty_store.add_penalty("u1", "Abuse", "admin1")

    # Attach penalty to user
    fake_users[0]["penalties"].append(p)

    updated = user_service.deactivate_penalty(
        penalty_id=p["penalty_id"],
        admin_id="adminX"
    )

    assert updated is not None
    assert updated["active"] is False

    # User copy updated
    assert fake_users[0]["penalties"][0]["active"] is False
