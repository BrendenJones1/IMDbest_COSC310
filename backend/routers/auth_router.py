from fastapi import APIRouter, Depends

from backend.schemas.user_models_schema import TokenResponse, UserCreate, UserLogin, UserPublic
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserCreate):
    user = auth_service.register_user(payload)
    token = auth_service.create_access_token(user.id)
    return {"token": token, "user": user}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin):
    user = auth_service.authenticate_user(payload)
    token = auth_service.create_access_token(user.id)
    return {"token": token, "user": user}


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: UserPublic = Depends(auth_service.get_current_user)):
    return current_user
