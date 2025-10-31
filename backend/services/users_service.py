import uuid
from fastapi import HTTPException
from schemas.user import UserCreate, UserUpdate, UserPublic, User
from repositories.users_repo import load_users, save_users
from utils.security import hash_password, verify_password, create_access_token
from typing import List

def list_users() -> List[UserPublic]:
    return [UserPublic(**it) for it in load_users() or []]

def register(payload: UserCreate) -> str:
    users = load_users()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in users):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    if any(it.get("username").lower() == payload.username.strip().lower() for it in users):  # validate unique username
        raise HTTPException(status_code=409, detail="Username taken.")
    if any(it.get("email").lower() == payload.email.strip().lower() for it in users):  # validate email not in use
        raise HTTPException(status_code=409, detail="Email in use.")
    
    is_first_user = len(users) == 0
    role = "admin" if is_first_user else "user"  # first user to register is admin

    new_user = User(
        id=new_id, 
        username=payload.username.strip(), 
        email=payload.email.strip(),
        password_hash=hash_password(payload.password),
        role=role,
        penalties=[],
        reviews=[],
        watchlist=[]
    ).model_dump()
    users.append(new_user)
    save_users(users)
    return create_access_token(new_user["id"], new_user["role"])

def login(username: str, password: str) -> str:
    try:
        u = _internal_get_user(username)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid credentials") 
    if not verify_password(password, u["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_access_token(u["id"], u["role"])

def get_user_by_id(user_id: str) -> UserPublic:
    users = load_users() or []
    for it in users:
        if it.get("id") == user_id:
            return UserPublic(**it)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def get_user_by_username(username: str) -> UserPublic:
    users = load_users() or []
    for it in users:
        if it.get("username").lower() == username.lower():
            return UserPublic(**it)
    raise HTTPException(status_code=404, detail=f"User '{username}' not found")

def _internal_get_user(username: str) -> dict:
    users = load_users() or []
    for it in users:
        if it.get("username").lower() == username.lower():
            return it
    raise HTTPException(status_code=404, detail="User not found")

def update_user(user_id: str, payload: UserUpdate) -> UserPublic:
    users = load_users() or []

    for idx, it in enumerate(users):
        if it["id"] == user_id:
            stored = User(**it)
            update_data = payload.model_dump(exclude_unset=True)

            # Unique username validation
            if "username" in update_data:
                update_data["username"] = update_data["username"].strip()
                if any(u["username"].lower() == update_data["username"].lower() and u["id"] != user_id for u in users):
                    raise HTTPException(status_code=409, detail="Username taken.")

            # Unique email validation
            if "email" in update_data:
                update_data["email"] = update_data["email"].strip()
                if any(u["email"].lower() == update_data["email"].lower() and u["id"] != user_id for u in users):
                    raise HTTPException(status_code=409, detail="Email in use.")

            # Secure password handling
            if "password" in update_data:
                update_data["password_hash"] = hash_password(update_data.pop("password"))

            updated = stored.model_copy(update=update_data)
            users[idx] = updated.model_dump()
            save_users(users)
            return UserPublic(**updated.model_dump())

    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    users = load_users() or []
    new_users = [it for it in users if it.get("id") != user_id]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_users(new_users)

