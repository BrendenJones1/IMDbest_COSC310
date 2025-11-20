import bcrypt, jwt, os
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from pydantic_settings import BaseSettings
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer


class Settings(BaseSettings):
    """
    Central configuration for JWT and password hashing parameters.
    """
    JWT_SECRET: str = "dev"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    BCRYPT_ROUNDS: int = 12


settings = Settings()  # loads overrides from environment/.env if present
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(pw: str) -> str:
    """
    Hash a plaintext password using bcrypt and return the encoded hash.
    """
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(settings.BCRYPT_ROUNDS)).decode()


def verify_password(pw: str, hashed: str) -> bool:
    """
    Verify that a plaintext password matches the stored bcrypt hash.
    """
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def create_access_token(sub: str, role: str, token_version: int = 0) -> str:
    """
    Create a signed JWT containing user id, role, and token_version with an expiry.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = {
        "sub": sub,
        "role": role,
        "token_version": token_version,
        "exp": expire,  # enforce token expiry on decode
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )

    return encoded_jwt


def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode and validate a JWT from the Authorization header and return its claims.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(current_user: dict):
    """
    Enforce that the current user has admin role or raise a 403 error.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
