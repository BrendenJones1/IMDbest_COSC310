from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str = "user"
    penalties: List[str] = []
    reviews: List[str] = []
    watchlist: List[str] = []


class UserPublic(UserBase):
    pass


class UserInDB(UserBase):
    password_hash: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: UserPublic
