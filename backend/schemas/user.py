from typing import List, Literal, Optional, TypedDict
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from backend.schemas.review import ReviewOut

class User(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    role: Literal["admin", "user"] = "user"
    penalties: List[str]
    reviews: List[str]
    watchlist: List[str]
    token_version: int=0
    registered_at: datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Literal["admin", "user"]] = None
    penalties: Optional[List[str]] = None
    reviews: Optional[List[str]] = None
    watchlist: Optional[List[str]] = None

class UserPublic(BaseModel):
    id: str
    username: str
    email: str
    reviews: list = Field(default_factory=list)
    watchlist: list = Field(default_factory=list)
    registered_at: Optional[datetime] = None

    @field_serializer("registered_at", when_used="json")
    def serialize_registered_at(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        # datetime.isoformat() already includes timezone offsets when present.
        iso = value.isoformat()
        if iso.endswith("Z"):
            return iso[:-1] + "+00:00"
        return iso

class CurrentUser(TypedDict):
    username: str
    role: str
    token_version: int


class UserExportStats(BaseModel):
    reviewCount: int


class UserExport(BaseModel):
    user: UserPublic
    stats: UserExportStats
    reviews: List[ReviewOut]
