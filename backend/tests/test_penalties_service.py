from backend.services.penalties_service import PenaltiesService
import tempfile, os


def test_penalty_equivalence_partitions():
    """Equivalence partitioning around penalty states."""
    tmpfile = os.path.join(tempfile.gettempdir(), "penalties_test.json")
    service = PenaltiesService(tmpfile)

    # Partition 1: valid penalty creation (active entry)
    penalty = service.add_penalty(user_id=5, reason="spam", issued_by=10)
    assert penalty["active"] is True

    # Partition 2: user with no penalties should return empty list
    assert service.get_for_user(user_id=999) == []

    # Partition 3: deactivate existing penalty -> returns record
    revoked = service.deactivate_penalty(penalty["penalty_id"], revoked_by=11)
    assert revoked["active"] is False

    # Partition 4: deactivate already inactive/nonexistent penalty -> None
    assert service.deactivate_penalty(penalty["penalty_id"], revoked_by=11) is None
    assert service.deactivate_penalty(123456, revoked_by=11) is None

    # Partition 5: add second penalty for another user and ensure retrieval works
    second = service.add_penalty(user_id=6, reason="abuse", issued_by=10)
    user_penalties = service.get_for_user(user_id=6)
    assert user_penalties, "Expected at least one penalty for user 6"
    assert user_penalties[-1]["penalty_id"] == second["penalty_id"]
