from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.penalty import (
    PenaltyCreate,
    PenaltyDeactivateRequest,
    PenaltyOut,
    PenaltyUpdate,
)
from backend.services.penalties_service import PenaltiesService

router = APIRouter(prefix="/penalties", tags=["penalties"])
service = PenaltiesService()


@router.post("", response_model=PenaltyOut, status_code=status.HTTP_201_CREATED)
def issue_penalty(payload: PenaltyCreate):
    """
    Create and record a new penalty against a user based on the provided details.
    """
    return service.add_penalty(
        user_id=payload.user_id,
        reason=payload.reason,
        issued_by=payload.issued_by,
        source_flag_id=payload.source_flag_id,
    )


@router.get("", response_model=List[PenaltyOut])
def list_penalties(user_id: int | None = Query(default=None, ge=1)):
    """
    List penalties, optionally restricted to those belonging to a specific user.
    """
    if user_id is not None:
        return service.get_for_user(user_id)  # scoped lookup for a single user's penalties
    return service.get_all()


@router.post("/{penalty_id}/deactivate", response_model=PenaltyOut)
def deactivate_penalty(penalty_id: int, payload: PenaltyDeactivateRequest):
    """
    Deactivate an active penalty, recording which admin revoked it.
    """
    penalty = service.deactivate_penalty(penalty_id, revoked_by=payload.revoked_by)

    if not penalty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active penalty not found")

    return penalty


@router.patch("/{penalty_id}", response_model=PenaltyOut)
def update_penalty(penalty_id: int, payload: PenaltyUpdate):
    penalty = service.update_penalty(
        penalty_id,
        reason=payload.reason,
        issued_by=payload.issued_by,
        source_flag_id=payload.source_flag_id,
    )

    if not penalty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Penalty not found")

    return penalty
