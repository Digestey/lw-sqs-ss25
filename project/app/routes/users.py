# app/routes/users.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from services.auth_service import (
    authenticate_user,
    create_access_token,
    Token,
    register_user
)
from util.logger import get_logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = get_logger("Users")

# User registration


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/api/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
        token = create_access_token(data={"sub": user.username})
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    return token


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    try:
        user = register_user(request.username, request.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
