from unittest.mock import patch, MagicMock
import bcrypt
import pytest

from app.services.database_service import add_user, delete_user, get_user


@patch("app.services.database_service.get_connection")
def test_add_user_success(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    add_user("testuser", "testpassword")

    assert mock_cursor.execute.called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_delete_user(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    delete_user("testuser")

    mock_cursor.execute.assert_called_with(
        "DELETE FROM users WHERE username=(%s)", ("testuser",))
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_get_user(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"username": "testuser", "password hash": "abc"}
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    user = get_user("testuser")
    assert user["username"] == "testuser"
    mock_cursor.execute.assert_called_once()
