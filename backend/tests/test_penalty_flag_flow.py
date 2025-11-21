from backend.services.flags_service import FlagsService
from backend.services.penalties_service import PenaltiesService
from contextlib import contextmanager


def test_flag_to_penalty_workflow():
    """
    Validate the end-to-end flow from creating a review flag to issuing a related penalty.
    """
    flags = FlagsService()
    penalties = PenaltiesService()

    # 1. User flags a review
    flag = flags.add_flag(review_id=5, flagger_id=12, flagged_user_id=8, reason="abusive")

    # 2. Admin approves it
    flags.update_flag_status(flag["flag_id"], "approved")

    # 3. Admin issues penalty derived from the approved flag
    penalty = penalties.add_penalty(
        user_id=flag["flagged_user_id"],
        reason=flag["reason"],
        issued_by=99,
    )

    assert penalty["user_id"] == 8
    assert penalty["issued_by"] == 99
    assert penalty["reason"] == "abusive"
