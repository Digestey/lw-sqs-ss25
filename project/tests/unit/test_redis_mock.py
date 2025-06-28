import pytest
from unittest.mock import patch, MagicMock
import json
import time

import app.services.redis_service as redis_service


@pytest.fixture
def mock_redis_client():
    with patch("app.services.redis_service.redis.Redis") as mock_redis_class:
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        yield mock_client


def test_create_redis_client_calls_with_env_vars(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "myhost")
    monkeypatch.setenv("REDIS_PORT", "1234")
    with patch("app.services.redis_service.redis.Redis") as mock_redis:
        redis_service.create_redis_client()
        mock_redis.assert_called_once_with(host="myhost", port=1234, db=0, decode_responses=True)


def test_get_redis_client_returns_new_client_instance():
    with patch("app.services.redis_service.create_redis_client") as mock_create:
        redis_service.get_redis_client()
        mock_create.assert_called_once()


def test_is_redis_healthy_returns_true_when_ping_success(mock_redis_client):
    mock_redis_client.ping.return_value = True
    assert redis_service.is_redis_healthy() is True
    mock_redis_client.ping.assert_called_once()


def test_is_redis_healthy_retries_and_returns_false(monkeypatch):
    # Patch sleep to avoid actual delay during tests
    monkeypatch.setattr(time, "sleep", lambda _: None)
    with patch("app.services.redis_service.get_redis_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.ping.side_effect = redis_service.redis.exceptions.ConnectionError("fail")
        mock_get_client.return_value = mock_client

        result = redis_service.is_redis_healthy(retries=3, delay=0)
        assert result is False
        assert mock_client.ping.call_count == 3


def test_get_state_returns_deserialized_state(mock_redis_client):
    sample_data = {"name": "bulbasaur", "pokemon_id": 1}
    mock_redis_client.get.return_value = json.dumps(sample_data)

    state = redis_service.get_state("client1")
    assert state == sample_data
    mock_redis_client.get.assert_called_once_with("quiz:client1")


def test_get_state_returns_none_if_no_state(mock_redis_client):
    mock_redis_client.get.return_value = None
    state = redis_service.get_state("client1")
    assert state is None


def test_set_state_sets_json_with_expiry(mock_redis_client):
    data = {"name": "charmander"}
    redis_service.set_state("client2", data)
    expected_key = "quiz:client2"
    mock_redis_client.setex.assert_called_once()
    args, kwargs = mock_redis_client.setex.call_args
    assert args[0] == expected_key
    assert args[1] == 1800
    assert json.loads(args[2]) == data


def test_clear_state_deletes_key(mock_redis_client):
    redis_service.clear_state("client3")
    mock_redis_client.delete.assert_called_once_with("quiz:client3")


def test_get_score_returns_int_or_zero(mock_redis_client):
    mock_redis_client.get.side_effect = ["100", None]
    score1 = redis_service.get_score("client4")
    score2 = redis_service.get_score("client5")
    assert score1 == 100
    assert score2 == 0


def test_increment_score_increments_and_sets_expiry(mock_redis_client):
    redis_service.increment_score("client6", value=50)
    expected_key = "quiz:client6:score"
    mock_redis_client.incrby.assert_called_once_with(expected_key, 50)
    mock_redis_client.expire.assert_called_once_with(expected_key, 1800)


def test_reset_score_deletes_score_key(mock_redis_client):
    redis_service.reset_score("client7")
    mock_redis_client.delete.assert_called_once_with("quiz:client7:score")
