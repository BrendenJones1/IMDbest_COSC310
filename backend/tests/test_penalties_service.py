import pytest
from backend.services.penalties_service import PenaltiesService


@pytest.fixture()
def penalties_service(tmp_path):
    """
    Provide a PenaltiesService instance backed by a temporary JSON file.
    """
    file_path = tmp_path / "penalties.json"
    return PenaltiesService(str(file_path))


def test_add_and_revoke_penalty(penalties_service):
    """
    A penalty can be created as active and later revoked with the correct metadata.
    """
    penalty = penalties_service.add_penalty(user_id=5, reason="spam", issued_by=10)
    assert penalty["user_id"] == 5
    assert penalty["issued_by"] == 10
    assert penalty["active"] is True

    revoked = penalties_service.deactivate_penalty(penalty["penalty_id"], revoked_by=11)
    assert revoked["active"] is False
    assert revoked["revoked_by"] == 11


@pytest.mark.parametrize("source_flag_id", [None, 42])
def test_add_penalty_source_flag_partitions(penalties_service, source_flag_id):
    """
    Penalties may optionally be linked to a source flag, including the None case.
    """
    penalty = penalties_service.add_penalty(
        user_id=1,
        reason="abuse",
        issued_by=2,
        source_flag_id=source_flag_id,
    )
    assert penalty["source_flag_id"] == source_flag_id


def test_deactivate_penalty_equivalence_partitions(penalties_service):
    """
    Deactivating penalties behaves consistently for active, inactive, and missing records.
    """
    penalty = penalties_service.add_penalty(user_id=7, reason="spam", issued_by=3)

    # Active penalty → should deactivate and return the updated record
    active_result = penalties_service.deactivate_penalty(penalty["penalty_id"], revoked_by=8)
    assert active_result is not None
    assert active_result["active"] is False

    # Already inactive penalty → should return None
    repeat_result = penalties_service.deactivate_penalty(penalty["penalty_id"], revoked_by=9)
    assert repeat_result is None

    # Non-existent penalty → should return None
    missing_result = penalties_service.deactivate_penalty(9999, revoked_by=9)
    assert missing_result is None


def test_update_penalty_mutates_fields(penalties_service):
    penalty = penalties_service.add_penalty(
        user_id=2,
        reason="old",
        issued_by=4,
        source_flag_id=None,
    )

    updated = penalties_service.update_penalty(
        penalty["penalty_id"],
        reason="new reason",
        issued_by=10,
        source_flag_id=99,
    )

    assert updated["reason"] == "new reason"
    assert updated["issued_by"] == 10
    assert updated["source_flag_id"] == 99
