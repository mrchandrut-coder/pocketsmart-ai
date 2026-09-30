from datetime import datetime, timedelta, timezone
import os
import secrets
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

from database import get_user_by_username

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_COOKIE = "access_token"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user_by_username(username)
    if user is None or user["disabled"] or not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire_at = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload.update({"exp": expire_at})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request) -> dict:
    authorization = request.headers.get("authorization", "")
    bearer_token = authorization[7:].strip() if authorization.lower().startswith("bearer ") else None
    token = request.cookies.get(ACCESS_TOKEN_COOKIE) or bearer_token
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = claims.get("sub")
        if not isinstance(username, str) or not username:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc
    user = get_user_by_username(username)
    if user is None or user["disabled"]:
        raise credentials_error
    return user
