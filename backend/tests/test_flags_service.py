import os
import tempfile
from unittest import mock
from contextlib import contextmanager

from backend.services.flags_service import FlagsService


def test_add_and_update_flag():
    """
    Verify a flag can be created in a temp store and have its status updated.
    """
    tmpfile = os.path.join(tempfile.gettempdir(), "flags_test.json")
    service = FlagsService()
    service.file = tmpfile  # redirect backing file to an isolated temp path
    service._save([])

    flag = service.add_flag(review_id=2, flagger_id=5, flagged_user_id=8, reason="spam")
    assert flag["status"] == "pending"

    updated = service.update_flag_status(flag["flag_id"], "approved")
    assert updated["status"] == "approved"


def test_update_flag_status_with_mock(tmp_path):
    """
    Verify update_flag_status mutates the correct flag when using the repo.transaction()
    context manager. We provide a fake repo that yields an in-memory list so no filesystem
    IO happens and we can inspect the mutated list.
    """
    service = FlagsService(str(tmp_path / "flags.json"))

    in_memory_flags = [
        {"flag_id": 1, "status": "pending"},
        {"flag_id": 2, "status": "pending"},
    ]

    # Create a fake repo that exposes file_path (so _ensure_repo() won't replace it)
    # and a transaction() context manager that yields our in_memory_flags.
    class FakeRepo:
        def __init__(self, data, file_path):
            self._data = data
            self.file_path = file_path

        @contextmanager
        def transaction(self):
            # This mimics FlagsRepository.transaction: yield data, caller mutates it,
            # and on successful exit we'd persist. For the test we just yield the list.
            yield self._data

    # Attach the fake repo to the service and ensure service won't overwrite it
    service.repo = FakeRepo(in_memory_flags, service.file)

    # Act
    updated_flag = service.update_flag_status(2, "approved")

    # Assert: returned object is the same element in the in-memory list, and was mutated
    assert updated_flag is in_memory_flags[1]
    assert in_memory_flags[1]["status"] == "approved"
