"""Auth service unit tests"""
from unittest.mock import patch
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import pytest

import app.services.auth_service as auth
import app.services.database_service as db
from app.models.token import Token


def test_check_credentials_valid():
    """Check if credentials are valid when ehey are supposed to be"""
    assert auth.check_credentials("validuser", "validpass123") is True


@pytest.mark.parametrize("username,password", [
    ("usr", "validpass123"),  # short username
    ("validuser", "short"),   # short password
    ("", ""),                 # both empty
])
def test_check_credentials_invalid(username, password):
    """Check if credentials are invalid """
    assert auth.check_credentials(username, password) is False


def test_register_user_valid():
    """Check if registration works"""
    result = auth.register_user("validuser", "validpass123")
    assert isinstance(result, bytes)
    assert bcrypt.checkpw("validpass123".encode(), result)


def test_register_user_invalid():
    """Check if registration detects invalid username/password"""
    with pytest.raises(Exception) as excinfo:
        auth.register_user("usr", "pwd")
    assert "Registration failed" in str(excinfo.value)


def test_authenticate_user_valid():
    """Check if authentication works without a hitch"""
    test_password = "validpass123"
    hashed = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt())
    db_user = {
        "id": 1,
        "username": "user",
        "password_hash": hashed,
        "created_at": datetime.now()
    }
    user = auth.authenticate_user(db_user, test_password)
    assert user.username == "user"


@patch("bcrypt.checkpw", return_value=False)
def test_authenticate_user_invalid_password(mock_checkpw):
    """Check if invalid credentials are blocked by authentication"""
    db_user = {
        "id": 1,
        "username": "user",
        "password_hash": "wrong",
        "created_at": datetime.now()
    }
    with pytest.raises(Exception) as excinfo:
        auth.authenticate_user(db_user, "invalid")
    assert "Invalid credentials" in str(excinfo.value)


def test_authenticate_user_missing_fields():
    """Check if missing credentials are blocked by authentication"""
    db_user = {
        "id": 1,
        "username": "",
        "password_hash": "",
        "created_at": datetime.now()
    }
    with pytest.raises(Exception) as excinfo:
        auth.authenticate_user(db_user, "")
    assert "Invalid credentials" in str(excinfo.value)


def test_create_access_token_and_get_user(monkeypatch):
    """Check if tokens are created correctly. Mock db access."""
    test_username = "testuser"
    test_secret = "testsecret"

    monkeypatch.setattr(auth, "SECRET_KEY", test_secret)

    # Provide all required fields that UserInDb expects
    dummy_user = {
        "id": 1,
        "username": test_username,
        "password_hash": "fakehash",
        "created_at": datetime.now(),
    }

    # DB mock
    monkeypatch.setattr(auth, "get_user", lambda cnn, username: dummy_user)

    token_obj = auth.create_access_token(
        {"sub": test_username}, timedelta(minutes=5))
    assert isinstance(token_obj, Token)

    decoded_user = auth.get_user_from_token(
        token_obj.access_token, db_conn=None)
    assert decoded_user.username == test_username


def test_get_user_from_token_invalid(monkeypatch):
    """Check if invalid token is rejected."""
    monkeypatch.setattr(auth, "SECRET_KEY", "correctkey")

    invalid_token = jwt.encode({"sub": "user"}, "wrongkey", algorithm="HS256")

    # Mock get_user to avoid needing a real DB call
    monkeypatch.setattr(db, "get_user", lambda cnn,
                        username: {"username": username})

    with pytest.raises(Exception) as excinfo:
        auth.get_user_from_token(invalid_token, db_conn=None)

    assert "Invalid token" in str(excinfo.value)
