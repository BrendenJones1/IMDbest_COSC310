from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FlagCreate(BaseModel):
    review_id: int = Field(..., ge=1)
    flagger_id: int = Field(..., ge=1)
    flagged_user_id: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)


class FlagStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1)


class FlagOut(BaseModel):
    flag_id: int
    review_id: int
    flagger_id: int
    flagged_user_id: int
    reason: str
    status: str
    date_created: Optional[datetime] = None
