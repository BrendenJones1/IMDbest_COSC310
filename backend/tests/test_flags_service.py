from backend.services.flags_service import FlagsService
from backend.services.penalties_service import PenaltiesService
import tempfile, os

def test_add_and_update_flag():
    tmpfile = os.path.join(tempfile.gettempdir(), "flags_test.json")
    service = FlagsService()
    service.file = tmpfile  # redirect to temp file
    service._save([])

    flag = service.add_flag(review_id=2, flagger_id=5, flagged_user_id=8, reason="spam")
    assert flag["status"] == "pending"

    updated = service.update_flag_status(flag["flag_id"], "approved")
    assert updated["status"] == "approved"