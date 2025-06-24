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
from app.services.database_service import get_user, add_user, get_connection
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
    db_conn = None
    logger.info("Login attempt for user: %s", form_data.username)
    try:
        db_conn = get_connection()
        db_user = get_user(db_conn, form_data.username)
        if db_user is None:
            logger.warning("Login failed: User %s not found", form_data.username)
            raise HTTPException(
                status_code=401, detail="Invalid username or password")
        user = authenticate_user(db_user, form_data.password)
        if not user:
            logger.warning("Login failed: Invalid password for user %s", form_data.username)
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_access_token(data={"sub": user.username})
    except HTTPException as e:
        logger.error("HTTPException during login for user %s: %s", form_data.username, e.detail)
        raise e
    except Exception as e:
        logger.error("Unexpected error during login for user %s: %s", form_data.username, e)
        # print("Exception: PRINT THE DAMN EXCEPTION HERE" + str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") from e
    finally:
        if db_conn:
            db_conn.close()
    return token


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Registers a new user.
    Args:
        request (RegisterRequest): Request

    Raises:
        HTTPException: _description_
    """
    db_conn = None
    logger.info("Register attempt for new user: %s", request.username)
    try:
        db_conn = get_connection()
        add_user(db_conn, request.username, register_user(
            request.username, request.password))
        logger.info("User registered successfully: %s", request.username)
    except Exception as e:
        logger.error("Error during registration for user %s: %s", request.username, e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    finally:
        if db_conn:
            db_conn.close()
