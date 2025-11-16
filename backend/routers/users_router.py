from fastapi import APIRouter, Depends, HTTPException, status, Query
from schemas.user import UserCreate, UserUpdate, UserPublic
from backend.services.users_service import user_service
from utils.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/users", tags=["Users"])

security = HTTPBearer()

# --- Helper Dependency ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # extract the raw JWT
    return decode_access_token(token)

# --- ROUTES ---
# -------------------------------
# GET USERS
# -------------------------------
@router.get("/", response_model=list[UserPublic])
def list_users():
    return user_service.list_users()
# -------------------------------
# REGISTER
# -------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate):
    """Register a new user and return a JWT token and User."""
    return user_service.register(payload)
# -------------------------------
# LOGIN
# -------------------------------
@router.post("/login")
def login(username: str, password: str):
    """Login user and return JWT token and User."""
    return user_service.login(username, password)
# -------------------------------
# UPDATE USER
# -------------------------------
@router.put("/{user_id}", response_model=UserPublic)
def update_user(user_id: str, payload: UserUpdate, current=Depends(get_current_user)):
    """Update user info. Admins can edit any user; users can edit themselves."""
    if current["role"] != "admin" and current["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user_service.update_user(user_id, payload)
# -------------------------------
# SEARCH USERS BY USERNAME
# -------------------------------
@router.get("/search")
def search_users(username: str | None = Query(None)):
    ## return 200 and empty list if no matches
    results = user_service.search_users(username=username)
    return results
# -------------------------------
# GET USER BY ID
# -------------------------------
@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: str):
    """Retrieve a single user by ID."""
    return user_service.get_user_by_id(user_id)

