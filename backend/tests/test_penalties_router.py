import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import penalties_router
from backend.services.penalties_service import PenaltiesService


client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_penalties_store(tmp_path, monkeypatch):
    fake_file = tmp_path / "penalties.json"
    fake_file.write_text("[]")
    service = PenaltiesService(path=str(fake_file))
    monkeypatch.setattr(penalties_router, "service", service)
    return service


def test_issue_and_list_penalties():
    create_payload = {
        "user_id": 42,
        "issued_by": 1,
        "reason": "abusive behaviour",
        "source_flag_id": 10,
    }
    res_create = client.post("/penalties", json=create_payload)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["penalty_id"] == 1
    assert created["active"] is True
    assert created["user_id"] == 42
    assert created["source_flag_id"] == 10

    res_all = client.get("/penalties")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 1

    res_user = client.get("/penalties", params={"user_id": 42})
    assert res_user.status_code == 200
    assert len(res_user.json()) == 1


def test_deactivate_penalty():
    res_create = client.post(
        "/penalties",
        json={
            "user_id": 99,
            "issued_by": 3,
            "reason": "spam",
            "source_flag_id": None,
        },
    )
    penalty_id = res_create.json()["penalty_id"]

    res_deactivate = client.post(
        f"/penalties/{penalty_id}/deactivate",
        json={"revoked_by": 3},
    )
    assert res_deactivate.status_code == 200
    payload = res_deactivate.json()
    assert payload["active"] is False
    assert payload["revoked_by"] == 3
