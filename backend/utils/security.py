import bcrypt, jwt, os
from datetime import datetime, timedelta, timezone
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str = "dev"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    BCRYPT_ROUNDS: int = 12

settings = Settings()  # loads from .env if present

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(settings.BCRYPT_ROUNDS)).decode()

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def create_access_token(sub: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": sub,
        "role": role,
        "exp": expire  # JWT lib converts this correctly
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG
    )

    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
