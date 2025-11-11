from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.penalty import PenaltyCreate, PenaltyDeactivateRequest, PenaltyOut
from backend.services.penalties_service import PenaltiesService

router = APIRouter(prefix="/penalties", tags=["penalties"])
service = PenaltiesService()


@router.post("", response_model=PenaltyOut, status_code=status.HTTP_201_CREATED)
def issue_penalty(payload: PenaltyCreate):
    return service.add_penalty(
        user_id=payload.user_id,
        reason=payload.reason,
        issued_by=payload.issued_by,
        source_flag_id=payload.source_flag_id,
    )


@router.get("", response_model=List[PenaltyOut])
def list_penalties(user_id: int | None = Query(default=None, ge=1)):
    if user_id is not None:
        return service.get_for_user(user_id)
    return service.get_all()


@router.post("/{penalty_id}/deactivate", response_model=PenaltyOut)
def deactivate_penalty(penalty_id: int, payload: PenaltyDeactivateRequest):
    penalty = service.deactivate_penalty(penalty_id, revoked_by=payload.revoked_by)

    if not penalty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active penalty not found")

    return penalty
