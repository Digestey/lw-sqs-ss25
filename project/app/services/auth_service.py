"""
Module auth_service: Authentication Service

Handles everything authentication- and token-related.
However does NOT connect to the database.
"""
from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.user_in_db import UserInDb
from app.models.token import Token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MIN_USERNAME_LENGTH = 5
MIN_PASSWORD_LENGTH = 8
MAX_STRING_LENGTH = 100

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")



def register_user(username, password):
    """Registers a new user."""
    if not check_credentials(username, password):
        raise HTTPException(status_code=400, detail="Registration failed")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed


def authenticate_user(db_user, plain_pw):
    """Verifies user credentials and returns the UserInDb model if valid."""
    username = db_user["username"]
    password_hash = db_user["password_hash"]

    if len(username) < 1 or len(password_hash) < 1:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')

    if not bcrypt.checkpw(plain_pw.encode('utf-8'), password_hash):
        print("credentials invalid")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print("authenticate user complete")
    return UserInDb(
        id=db_user["id"],
        username=username,
        password_hash=password_hash.decode() if isinstance(
            password_hash, bytes) else password_hash,
        created_at=db_user["created_at"]
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return Token(
        access_token=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM),
        token_type="bearer"
    )


def get_user_from_token(token: str):
    """Retrieves the user information from the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


def check_credentials(username: str, password: str):
    """Checks whether the credentials provided are according to the password requirements

    Args:
        username (str): username to be checked
        password (str): password to be checked

    Returns:
        (bool): Return True if both username and password are according to
        their respective requirements. False otherwise.
    """
    username_length = len(username)
    password_length = len(password)

    if username_length < MIN_USERNAME_LENGTH or username_length > MAX_STRING_LENGTH:
        return False

    if password_length < MIN_PASSWORD_LENGTH or password_length > MAX_STRING_LENGTH:
        return False
    return True
