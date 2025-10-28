from backend.services.penalties_service import PenaltiesService
import tempfile, os, json

def test_add_and_revoke_penalty():
    tmpfile = os.path.join(tempfile.gettempdir(), "penalties_test.json")
    service = PenaltiesService(tmpfile)

    # Add penalty
    penalty = service.add_penalty(user_id=5, reason="spam", issued_by=10)
    assert penalty["user_id"] == 5
    assert penalty["issued_by"] == 10
    assert penalty["active"] is True

    # Revoke penalty
    revoked = service.deactivate_penalty(penalty["penalty_id"], revoked_by=11)
    assert revoked["active"] is False
    assert revoked["revoked_by"] == 11