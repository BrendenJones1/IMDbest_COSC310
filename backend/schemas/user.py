from typing import List, Literal, Optional, TypedDict
from pydantic import BaseModel, Field

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

class CurrentUser(TypedDict):
    username: str
    role: str
    token_version: int