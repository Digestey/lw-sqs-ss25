from unittest.mock import patch, MagicMock
import pytest
import bcrypt
import mysql.connector

from app.services.database_service import add_user, delete_user, get_user


@patch("app.services.database_service.get_connection")
def test_add_user_success(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    add_user(mock_conn, "testuser", "testpassword")

    assert mock_cursor.execute.called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_add_user_integrity_error(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = mysql.connector.IntegrityError()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with pytest.raises(ValueError, match="Username already exists."):
        add_user(mock_conn, "existing_user", "password")

    mock_cursor.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_delete_user(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor 

    mock_cursor.rowcount = 1

    delete_user(mock_conn, "testuser")

    mock_cursor.execute.assert_called_with(
        "DELETE FROM users WHERE username = %s", ("testuser",)
    )
    mock_conn.commit.assert_called_once()
    # No need to call cursor.close because 'with' context manager auto-closes


@patch("app.services.database_service.get_connection")
def test_get_user_found(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1, "username": "testuser", "password_hash": "abc", "created_at": "now"
    }
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    user = get_user(mock_conn, "testuser")

    assert user["username"] == "testuser"
    mock_cursor.execute.assert_called_once()


@patch("app.services.database_service.get_connection")
def test_get_user_not_found(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    result = get_user(mock_conn, "nonexistent")
    assert result is None
    mock_cursor.close.assert_called()