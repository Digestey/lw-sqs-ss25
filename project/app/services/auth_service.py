from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


from services.database_service import add_user, get_user

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MIN_USERNAME_LENGTH = 5
MIN_PASSWORD_LENGTH = 8
MAX_STRING_LENGTH = 100

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDb(BaseModel):
    id: int
    username: str
    password_hash: str
    created_at: datetime


def register_user(username, password):
    """Registers a new user."""
    if not check_credentials(username, password):
        raise HTTPException(status_code=400, detail="Registration failed")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        add_user(username, hashed)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Registration failed: {str(e)}") from e


def authenticate_user(username, password):
    """Verifies user credentials and returns the UserInDb model if valid."""
    if (len(username) < 1 or  len(password) < 1):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user = get_user(username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserInDb(
        id=user["id"],
        username=user["username"],
        password_hash=user["password_hash"],
        created_at=user["created_at"]
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
        (bool): Return True if both username and password are according to their respective requirements. False otherwise.
    """
    username_length = len(username)
    password_length = len(password)
    
    if username_length < MIN_USERNAME_LENGTH or username_length > MAX_STRING_LENGTH:
        return False
    
    if password_length < MIN_PASSWORD_LENGTH or password_length > MAX_STRING_LENGTH:
        return False
    return True
