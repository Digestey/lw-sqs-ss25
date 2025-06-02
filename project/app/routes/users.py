"""
Module users:

Contains all api routes concerning user management.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    Token,
    register_user
)
from app.services.database_service import get_user, add_user
from app.util.logger import get_logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = get_logger("Users")

# User registration


class RegisterRequest(BaseModel):
    """Model for User
    """
    username: str
    password: str


@router.post("/api/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logs user in.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): form data. Defaults to Depends().

    Raises:
        HTTPException: If anything goes wrong, access is denied by default.

    Returns:
        str: Identification token (JWT).
    """
    try:
        db_user = get_user(form_data.username)
        if db_user is None:
            raise HTTPException(
                status_code=401, detail="Invalid username or password")
        user = authenticate_user(db_user, form_data.password)
        token = create_access_token(data={"sub": user.username})
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    return token


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Registers a new user.
    Args:
        request (RegisterRequest): Request

    Raises:
        HTTPException: _description_
    """
    try:
        add_user(request.username, register_user(
            request.username, request.password))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
