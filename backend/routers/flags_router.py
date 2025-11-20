from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.flag import FlagCreate, FlagOut, FlagStatusUpdate
from backend.services.flags_service import FlagsService

router = APIRouter(prefix="/flags", tags=["flags"])
service = FlagsService()


@router.post("", response_model=FlagOut, status_code=status.HTTP_201_CREATED)
def create_flag(payload: FlagCreate):
    """
    Create a new moderation flag for a specific review and return the stored flag.
    """
    return service.add_flag(
        review_id=payload.review_id,
        flagger_id=payload.flagger_id,
        flagged_user_id=payload.flagged_user_id,
        reason=payload.reason,
    )


@router.get("", response_model=List[FlagOut])
def list_flags(status_filter: str | None = Query(default=None, alias="status")):
    """
    List all flags, optionally filtered by their status via the 'status' query parameter.
    """
    flags = service.get_all_flags()

    if status_filter:
        lowered = status_filter.lower()  # normalize status for case-insensitive matching
        flags = [flag for flag in flags if flag.get("status", "").lower() == lowered]

    return flags


@router.get("/pending", response_model=List[FlagOut])
def list_pending_flags():
    """
    Return all flags that are currently in a pending review state.
    """
    return service.get_pending_flags()


@router.patch("/{flag_id}/status", response_model=FlagOut)
def update_flag_status(flag_id: int, payload: FlagStatusUpdate):
    """
    Update the status of a specific flag and return the updated record, or 404 if missing.
    """
    updated_flag = service.update_flag_status(flag_id, payload.status)

    if not updated_flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found")

    return updated_flag
