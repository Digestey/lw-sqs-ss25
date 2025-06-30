"""Database service highscore related unit tests."""
from unittest.mock import patch, MagicMock
import pytest

from app.services.database_service import (
    add_highscore,
    get_highscores,
    get_user_highscores,
    get_top_highscores
)


@patch("app.services.database_service.get_connection")
def test_add_highscore_success(mock_get_connection):
    """Check if you can add a highscore"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock SELECT user ID
    mock_cursor.fetchone.side_effect = [
        (1,),  # Result of SELECT id FROM users
        {"id": 42, "username": "testuser", "score": 100, "achieved_at": "2025-06-02"}
    ]

    mock_cursor.lastrowid = 42

    result = add_highscore(mock_conn, "testuser", 100)

    assert result["score"] == 100
    mock_cursor.execute.assert_any_call("SELECT id FROM users WHERE username = %s", ("testuser",))
    mock_cursor.execute.assert_any_call(
        "INSERT INTO highscores (user_id, score) VALUES (%s, %s)", (1, 100)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_add_highscore_user_not_found(mock_get_connection):
    """Check if you can not add a highscore if no user by the provided name was found."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None  # Simulate user not found

    with pytest.raises(ValueError, match="User not found"):
        add_highscore(mock_conn, "ghostuser", 100)

    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_get_highscores(mock_get_connection):
    """Check get highscores"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {"username": "user1", "score": 200, "achieved_at": "2025-06-02"},
        {"username": "user2", "score": 150, "achieved_at": "2025-06-01"},
    ]

    result = get_highscores(mock_conn)
    assert len(result) == 2
    assert result[0]["score"] == 200
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called()


@patch("app.services.database_service.get_connection")
def test_get_user_highscores(mock_get_connection):
    """Check get user highscores"""
    # Arrange
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Setup context manager return for `with conn.cursor(...) as cursor`
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock dictionary-style return
    mock_cursor.fetchall.return_value = [
        {"username": "user1", "score": 100, "achieved_at": "2025-06-01"},
        {"username": "user1", "score": 80, "achieved_at": "2025-05-30"},
    ]

    # Act
    result = get_user_highscores(mock_conn, "user1")

    # Assert
    assert len(result) == 2
    assert all(score["username"] == "user1" for score in result)
    mock_conn.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()


@patch("app.services.database_service.get_connection")
def test_get_top_highscores(mock_get_connection):
    """Test get top highscores"""
    # Arrange
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Setup context manager for cursor
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {"username": "user1", "score": 300, "achieved_at": "2025-06-01"},
        {"username": "user2", "score": 250, "achieved_at": "2025-06-01"},
    ]

    # Act
    result = get_top_highscores(mock_conn, limit=2)

    # Assert
    assert len(result) == 2
    assert result[0]["score"] == 300
    assert result[1]["username"] == "user2"

    mock_conn.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once_with(
        """
                SELECT u.username, h.score, h.achieved_at FROM highscores h
                JOIN users u ON h.user_id = u.id
                ORDER BY h.score DESC
                LIMIT %s
            """, (2,)
    )
    