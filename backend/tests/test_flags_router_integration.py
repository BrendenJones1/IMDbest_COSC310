import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import flags_router
from backend.services.flags_service import FlagsService


client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_flags_store(monkeypatch, tmp_path):
    fake_file = tmp_path / "flags.json"
    fake_file.write_text("[]")

    service = FlagsService(path=str(fake_file))
    # Replace the module-level service so routes use the temp file.
    monkeypatch.setattr(flags_router, "service", service)

    return service


def test_flags_router_create_list_update_flow():
    # Create flag
    res_create = client.post(
        "/flags",
        json={
            "review_id": 9,
            "flagger_id": 1,
            "flagged_user_id": 2,
            "reason": "spam",
        },
    )
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["status"] == "pending"

    # List pending (should include the new flag)
    res_pending = client.get("/flags/pending")
    assert res_pending.status_code == 200
    pending = res_pending.json()
    assert len(pending) == 1
    assert pending[0]["flag_id"] == created["flag_id"]

    # Update status
    res_update = client.patch(
        f"/flags/{created['flag_id']}/status",
        json={"status": "approved"},
    )
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "approved"

    # Filter by status now returns the updated flag
    res_filtered = client.get("/flags", params={"status": "approved"})
    assert res_filtered.status_code == 200
    filtered = res_filtered.json()
    assert len(filtered) == 1
    assert filtered[0]["status"] == "approved"
