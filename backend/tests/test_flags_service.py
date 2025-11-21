import os
import tempfile
from unittest import mock

from backend.services.flags_service import FlagsService

def test_add_and_update_flag():
    tmpfile = os.path.join(tempfile.gettempdir(), "flags_test.json")
    service = FlagsService()
    service.file = tmpfile  # redirect to temp file
    service._save([])

    flag = service.add_flag(review_id=2, flagger_id=5, flagged_user_id=8, reason="spam")
    assert flag["status"] == "pending"

    updated = service.update_flag_status(flag["flag_id"], "approved")
    assert updated["status"] == "approved"


def test_update_flag_status_with_mock(monkeypatch, tmp_path):
    service = FlagsService(str(tmp_path / "flags.json"))

    in_memory_flags = [
        {"flag_id": 1, "status": "pending"},
        {"flag_id": 2, "status": "pending"},
    ]
    monkeypatch.setattr(service, "_load", lambda: in_memory_flags)
    save_spy = mock.MagicMock()
    monkeypatch.setattr(service, "_save", save_spy)

    updated_flag = service.update_flag_status(2, "approved")

    assert updated_flag == in_memory_flags[1]
    assert updated_flag["status"] == "approved"
    save_spy.assert_called_once_with(in_memory_flags)
