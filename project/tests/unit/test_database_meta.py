import pytest
from unittest.mock import patch, MagicMock
from mysql.connector import Error
from app.services.database_service import is_database_healthy


@patch("app.services.database_service.mysql.connector.connect")
def test_is_database_healthy_success(mock_connect):
    """Test healthy database returns true"""
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_connect.return_value = mock_conn

    result = is_database_healthy(
        host="localhost",
        user="user",
        password="pass",
        database="testdb"
    )

    assert result is True
    mock_connect.assert_called_once()


@patch("app.services.database_service.mysql.connector.connect")
@patch("app.services.database_service.time.sleep")
def test_is_database_healthy_failure(mock_sleep, mock_connect):
    """Unhealthy database returns False"""
    mock_connect.side_effect = Error("Unable to connect")

    result = is_database_healthy(
        host="localhost",
        user="user",
        password="pass",
        database="testdb",
        retries=3,
        delay=1
    )

    assert result is False
    assert mock_connect.call_count == 3
    assert mock_sleep.call_count == 2  # retries - 1
