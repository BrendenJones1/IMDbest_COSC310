from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    review_text: Optional[str] = None

#change existing review
class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None

#output review
class ReviewOut(BaseModel):
    user_id: str
    rating: float
    review_text: Optional[str]
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
