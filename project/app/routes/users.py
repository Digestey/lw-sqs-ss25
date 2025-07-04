"""
Module users:

Contains all api routes concerning user management.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    refresh_token_pair,
    register_user
)
from app.services.database_service import get_user, add_user, get_connection
from app.util.logger import get_logger
from app.routes.highscores import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = get_logger("Users")

# User registration


class RegisterRequest(BaseModel):
    """Model for User
    """
    username: str
    password: str


def verify_credentials(username: str, password: str):
    conn = get_connection()
    try:
        db_user = get_user(conn, username)
        if db_user is None:
            logger.warning("Login failed: User %s not found", username)
            raise HTTPException(
                status_code=401, detail="Invalid username or password")

        user = authenticate_user(db_user, password)
        if not user:
            logger.warning("Login failed: Invalid password")
            raise HTTPException(
                status_code=401, detail="Invalid username or password")
        return user
    finally:
        conn.close()


def set_login_cookies(response: Response, username: str):
    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})

    response.set_cookie(
        key="access_token",
        value=access_token.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=1800,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604_800, # 7 days
        path="/"
    )


@router.post("/api/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route that returns access and refresh tokens as HTTP-only cookies."""
    logger.info("Login attempt for user: %s", form_data.username)
    try:
        user = verify_credentials(form_data.username, form_data.password)
        set_login_cookies(response, user.username)
    except HTTPException as e:
        logger.error("HTTPException during login for user %s: %s",
                     form_data.username, e.detail)
        raise
    except Exception as e:
        logger.error("Unexpected error during login for user %s: %s",
                     form_data.username, e)
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}") from e


@router.post("/api/token/refresh")
def refresh_token(response: Response, request: Request):
    db_conn = None
    try:
        db_conn = get_connection()
        old_token = request.cookies.get("refresh_token")
        if not old_token:
            raise HTTPException(
                status_code=401, detail="Missing refresh token")

        access_token, new_refresh_token, username = refresh_token_pair(
            old_token, db_conn)

        response.set_cookie("access_token", access_token, httponly=True,
                            secure=True, samesite="strict", max_age=1800, path="/")
        response.set_cookie("refresh_token", new_refresh_token, httponly=True,
                            secure=True, samesite="strict", max_age=7 * 24 * 60 * 60, path="/")
        return {"message": f"Token refreshed for {username}"}
    finally:
        if db_conn:
            db_conn.close()


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
        logger.error("Error during registration for user %s: %s",
                     request.username, e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    finally:
        if db_conn:
            db_conn.close()


@router.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out successfully"}


@router.get("/api/username")
async def get_username(current_user: dict = Depends(get_current_user_from_cookie)):
    return current_user
