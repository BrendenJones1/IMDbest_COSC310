from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

#create review
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=10)
    review_text: Optional[str] = None

#change existing review
class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=10)
    review_text: Optional[str] = None

#output review
class ReviewOut(BaseModel):
    user_id: str
    rating: int
    review_text: Optional[str]
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
