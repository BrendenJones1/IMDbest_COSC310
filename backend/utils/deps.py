from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security import decode_token
from typing import TypedDict
from backend.services import users_service as user_service
from backend.schemas import CurrentUser

auth_scheme = HTTPBearer(auto_error=True)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> CurrentUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token.credentials)
        username: str | None = payload.get("sub")
        role: str = payload.get("role")
        token_version: int = payload.get("token_version", 0)

        user = user_service._internal_get_user(username)
        if user is None:
            raise credentials_error

        # 🔑 KEY PART: if versions don't match, treat token as invalid
        if user.token_version != token_version:
            raise credentials_error
        
        return {"username": username, "role": role, "token_version": token_version}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
