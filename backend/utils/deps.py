from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security import decode_token
from typing import TypedDict

auth_scheme = HTTPBearer(auto_error=True)

class CurrentUser(TypedDict):
    id: str
    role: str

def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> CurrentUser:
    try:
        payload = decode_token(token.credentials)
        return {"id": payload["sub"], "role": payload["role"]}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
