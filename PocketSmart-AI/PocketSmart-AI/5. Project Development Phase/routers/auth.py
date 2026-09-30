import os
import sqlite3
from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import (
    ACCESS_TOKEN_COOKIE,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from database import create_user, list_recommendations
from models import Token, UserCreate

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        create_user(user.username, user.email, user.full_name, get_password_hash(user.password))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Username or email is already registered") from exc
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax",
        path="/",
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/", samesite="lax")
    return response

@router.post("/logout")
async def logout_api():
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/", samesite="lax")
    return response

@router.get("/session-info")
async def session_info(user: dict = Depends(get_current_user)):
    return {"status": "active", "username": user["username"]}

@router.get("/session-data")
async def session_data(user: dict = Depends(get_current_user)):
    return {"recommendations": len(list_recommendations(user["id"]))}