from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PenaltyCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    issued_by: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)
    source_flag_id: Optional[int] = Field(None, ge=1)


class PenaltyDeactivateRequest(BaseModel):
    revoked_by: int = Field(..., ge=1)


class PenaltyOut(BaseModel):
    penalty_id: int
    user_id: int
    issued_by: int
    reason: str
    source_flag_id: Optional[int] = None
    date_issued: datetime
    active: bool
    date_revoked: Optional[datetime] = None
    revoked_by: Optional[int] = None
