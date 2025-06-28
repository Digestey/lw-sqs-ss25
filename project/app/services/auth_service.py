"""
Module auth_service: Authentication Service

Handles everything authentication- and token-related.
However does NOT connect to the database directly. only via imports from the database service.
"""
from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.user_in_db import UserInDb
from app.models.token import Token
from app.services.database_service import get_user

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MIN_USERNAME_LENGTH = 5
MIN_PASSWORD_LENGTH = 8
MAX_STRING_LENGTH = 100

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def register_user(username, password):
    """Registers a new user by validating credentials and hashing the password.

    Args:
        username (str): The desired username.
        password (str): The user's plain-text password.

    Raises:
        HTTPException: If the credentials do not meet the required standards.

    Returns:
        bytes: The hashed password using bcrypt.
    """
    if not check_credentials(username, password):
        raise HTTPException(status_code=400, detail="Registration failed")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed


def authenticate_user(db_user, plain_pw):
    """Authenticates a user by checking the provided password against the stored hash.

    Args:
        db_user (dict): A dictionary containing user data from the database.
        plain_pw (str): The plain-text password for veryfication.

    Raises:
        HTTPException: In case the credentials are invalid or missing.

    Returns:
        UserInDb: The authenticated user data wrapped in a UserInDb model.
    """
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
    """Creates a JWT access token with an optional expiration.

    Args:
        data (dict): The payload to encode into the token.
        expires_delta (timedelta | None, optional): The duration before the token expires. 
            Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        Token: A Token object containing the access token and its type.
    """
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


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """Creates a JWT refresh token with an optional expiration (defaults to 7 days).

    Args:
        data (dict): The payload to encode into the token.
        expires_delta (timedelta | None, optional): Custom expiration time. Defaults to 7 days.

    Returns:
        Token: A Token object containing the refresh token and its type.
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return Token(
        access_token=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM),
        token_type="bearer"
    )


def refresh_token_pair(refresh_token: str, db_conn) -> tuple[str, str, str]:
    """Validates a refresh token and issues a new access and refresh token pair.

    Args:
        refresh_token (str): The JWT refresh token to verify.
        db_conn: The active database connection or session.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        tuple[str, str, str]: A tuple containing (access_token, refresh_token, username).
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token")
    except JWTError as exc:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token") from exc
    db_user = get_user(db_conn, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    return access_token, new_refresh_token, username


def get_user_from_token(token: str, db_conn) -> UserInDb:
    """Parses a JWT access token to extract the user and return user data.

    Args:
        token (str): The JWT access token.
        db_conn: The active database connection or session.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.

    Returns:
        UserInDb: The user information loaded into the UserInDb model.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Query the DB for this user
        user = get_user(db_conn, username)  # From database_service
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return UserInDb(**user)
    except jwt.JWTError as e:
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
