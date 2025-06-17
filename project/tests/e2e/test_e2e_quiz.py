import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.routes.frontend import sessions
from app.models.quiz_info import QuizInfo


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


@patch("app.routes.frontend.fetch_pokemon")
def test_correct_guess(mock_fetch, client: TestClient, test_pokemon, test_session_header):
    mock_fetch.return_value = test_pokemon
    sessions["test-session-1"] = test_pokemon  # manually inject session

    response = client.post("/quiz", data={"guess": "Pikachu"}, headers=test_session_header)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert "winner" in data["message"].lower()


@patch("app.routes.frontend.fetch_pokemon")
def test_wrong_guess(mock_fetch, client: TestClient, test_pokemon, test_session_header):
    mock_fetch.return_value = test_pokemon
    sessions["test-session-1"] = test_pokemon

    response = client.post("/quiz", data={"guess": "Charmander"}, headers=test_session_header)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert "incorrect" in data["message"].lower()


@patch("app.routes.frontend.fetch_pokemon")
def test_creates_new_session(mock_fetch, client: TestClient, test_pokemon, test_session_header):
    mock_fetch.return_value = test_pokemon

    # Clear previous session
    sessions.pop("test-session-1", None)
    assert "test-session-1" not in sessions

    response = client.post("/quiz", data={"guess": "Wrong"}, headers=test_session_header)
    assert response.status_code == 200
    assert "testclient" in sessions


def test_quiz_requires_form_data(client: TestClient, test_session_header):
    response = client.post("/quiz", headers=test_session_header)  # No 'guess' field
    assert response.status_code == 422  # Unprocessable Entity

