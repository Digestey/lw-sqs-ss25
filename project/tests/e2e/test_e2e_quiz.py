import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models.quiz_info import QuizInfo
from app.services.redis_service import set_state, get_state, clear_state


@pytest.fixture
def test_pokemon():
    return QuizInfo(
        name="pikachu",
        pokemon_id=25,
        height=4,
        weight=60,
        stats={"Speed": 90},
        types=["Electric"],
        entry="A mouse that shocks enemies."
    )


@pytest.fixture
def test_session_header():
    return {"X-Session-ID": "test-session-1"}


@pytest.fixture
def mock_sessions():
    with patch("app.routes.frontend.sessions", {}) as mock_store:
        yield mock_store


def test_wrong_guess(client, test_session_header):
    # Arrange: same setup, but guessing wrong
    set_state("test-session-1", {
        "name": "Bulbasaur",
        "score": 0,
        "pokemon_id": 1,  # Still Bulbasaur
        "answered": False
    })

    response = client.post(
        "/api/quiz", data={"guess": "Charmander"}, headers=test_session_header)

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["score"] == 0


def test_correct_guess(client, test_session_header):
    # Arrange: simulate state with Bulbasaur as current Pokémon
    set_state("test-session-1", {
        "name": "Bulbasaur",
        "score": 0,
        "pokemon_id": 1,  # Bulbasaur
        "answered": False
    })

    # Act: guessing correctly
    response = client.post(
        "/api/quiz", data={"guess": "Bulbasaur"}, headers=test_session_header)

    # Assert
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert data["correct"] is True
    assert data["score"] == 25


def test_creates_new_session(client, test_session_header):
    # Arrange: clear any old state
    clear_state("test-session-1")

    # Act: make a guess without existing state
    response = client.post(
        "/api/quiz", data={"guess": "Wrong"}, cookies={"quiz_session_id": "test-session-1"}, headers=test_session_header)

    # Assert: state should be created
    assert response.status_code == 200
    state = get_state("test-session-1")
    assert state is not None
    assert "score" in state
    assert "pokemon_id" in state


def test_quiz_requires_form_data(client: TestClient, test_session_header):
    response = client.post("/api/quiz", headers=test_session_header)
    assert response.status_code == 422
