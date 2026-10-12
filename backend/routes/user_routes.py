"""
==========================================================
AI JobAgent - User API Routes
Author : Beere Vishnu Sai
Description:
    FastAPI router for user authentication, registration,
    and profile management.
==========================================================
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel, EmailStr
from users.user_service import user_service

router = APIRouter(prefix="/user", tags=["User"])

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(payload: RegisterPayload):
    try:
        return user_service.register_user(payload.email, payload.password, payload.full_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(payload: LoginPayload):
    try:
        return user_service.login_user(payload.email, payload.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))



@router.get("/me")
def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header.")
    token = authorization.split(" ")[1]
    user = user_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return {"user": user}
