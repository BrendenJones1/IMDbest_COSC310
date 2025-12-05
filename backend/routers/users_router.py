from fastapi import APIRouter, Depends, HTTPException, status, Query
from backend.schemas.user import UserCreate, UserUpdate, UserPublic, CurrentUser
from backend.services.users_service import user_service
from backend.utils.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/users", tags=["Users"])

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Decode the bearer token, look up the user, and return a CurrentUser dict.
    """
    token = credentials.credentials  # raw JWT from Authorization header

    # Decode JWT into payload: {"sub": user_id, "role": ..., "token_version": ...}
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload (missing sub)",
        )

    # Look up the full user by ID (UserPublic)
    user: UserPublic | None = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # We take role and token_version from the JWT payload,
    # because UserPublic doesn't carry those fields.
    role = payload.get("role", "user")
    token_version = payload.get("token_version", 0)

    return {
        "sub": user.id,
        "username": user.username,
        "role": role,
        "token_version": token_version,
    }


@router.get("/", response_model=list[UserPublic])
def list_users():
    """
    Return a list of all registered users.
    """
    return user_service.list_users()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate):
    """
    Register a new user account and return the created user with an access token.
    """
    return user_service.register(payload)


@router.post("/login")
def login(username: str, password: str):
    """
    Authenticate a user and return an access token with the associated user.
    """
    return user_service.login(username, password)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user=Depends(get_current_user)):
    """
    Terminate the user's active sessions by invalidating existing tokens.
    """
    current_user.token_version += 1  # increment to invalidate all existing JWTs for this user
    user_service.save_user(current_user)
    return


@router.put("/{user_id}", response_model=UserPublic)
def update_user(user_id: str, payload: UserUpdate, current=Depends(get_current_user)):
    """
    Update a user's profile; admins can edit any user, others can only edit themselves.
    """
    if current["role"] != "admin" and current["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")  # enforce role-based access control
    return user_service.update_user(user_id, payload)


@router.get("/search")
def search_users(username: str | None = Query(None)):
    """
    Search for users by (partial) username, returning an empty list when no matches are found.
    """
    results = user_service.search_users(username=username)
    return results


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: str):
    """
    Retrieve a single user by their unique identifier.
    """
    return user_service.get_user_by_id(user_id)

from backend.schemas.user import UserExport, UserExportStats, CurrentUser
from backend.schemas.review import ReviewOut
from backend.services.review_service import ReviewService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

@router.get("/me/export", response_model=UserExport)
def export_my_data(current = Depends(get_current_user)):
    """
    Export the authenticated user's data (public profile + review stats + reviews).
    """
    user: UserPublic | None = user_service.get_user_by_username(current["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # ✅ Unpack the (reviews, metadata) tuple
    user_reviews, _ = ReviewService.get_reviews_by_user_id(user_id=user.id)

    export_payload = UserExport(
        user=user,
        stats=UserExportStats(reviewCount=len(user_reviews)),
        reviews=user_reviews,
    )

    return JSONResponse(
        content=jsonable_encoder(export_payload),
        headers={
            "Content-Disposition": 'attachment; filename="my-data.json"',
        },
    )
