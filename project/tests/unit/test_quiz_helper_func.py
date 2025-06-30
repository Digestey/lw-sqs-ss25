import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

from app.routes.quiz import (
    get_or_create_session_id,
    get_or_init_state,
    create_correct_response,
    create_incorrect_response,
    set_session_cookie,
)
from app.models.quiz_info import QuizInfo

### --- Tests for get_or_create_session_id --- ###

def test_get_or_create_session_id_existing_cookie():
    mock_request = MagicMock(Request)
    mock_request.cookies = {"quiz_session_id": "existing-id"}
    session_id = get_or_create_session_id(mock_request)
    assert session_id == "existing-id"

def test_get_or_create_session_id_no_cookie():
    mock_request = MagicMock(Request)
    mock_request.cookies = {}
    session_id = get_or_create_session_id(mock_request)
    uuid.UUID(session_id)  # will raise ValueError if invalid
    assert isinstance(session_id, str)

### --- Tests for get_or_init_state --- ###

@patch("app.routes.quiz.set_state")
@patch("app.routes.quiz.fetch_pokemon")
@patch("app.routes.quiz.get_state")
def test_get_or_init_state_existing(get_state, fetch_pokemon, set_state):
    get_state.return_value = {"name": "Pikachu", "score": 5}
    result = get_or_init_state("session123")
    assert result == {"name": "Pikachu", "score": 5}
    fetch_pokemon.assert_not_called()
    set_state.assert_not_called()


@patch("app.routes.quiz.set_state")
@patch("app.routes.quiz.fetch_pokemon")
@patch("app.routes.quiz.get_state")
def test_get_or_init_state_new(mock_get_state, mock_fetch_pokemon, mock_set_state):
    mock_get_state.return_value = None

    # Create a real QuizInfo instance
    quiz_info = QuizInfo(
        name="Bulbasaur",
        pokemon_id=1,
        height=7,
        weight=69,
        stats={"hp": 45, "attack": 49},
        types=["Grass", "Poison"],
        entry="A strange seed was planted on its back at birth."
    )
    mock_fetch_pokemon.return_value = quiz_info

    state = get_or_init_state("session123")

    assert state["name"] == "Bulbasaur"
    assert state["types"] == ["Grass", "Poison"]
    assert state["score"] == 0
    assert "entry" in state

    mock_set_state.assert_called_once_with("session123", state)

### --- Tests for create_correct_response --- ###

def test_create_correct_response():
    response = create_correct_response(10)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert response.body == b'{"correct":true,"message":"Ding Ding Ding! We have a winner!","score":10}'

### --- Tests for create_incorrect_response --- ###

def test_create_incorrect_response():
    response = create_incorrect_response(3)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert response.body == b'{"correct":false,"message":"That is incorrect. Another hint has been added to the entry.","hint":"","score":3}'

### --- Tests for set_session_cookie --- ###

def test_set_session_cookie_sets_cookie():
    response = JSONResponse(content={})
    session_id = "abc-123"
    set_session_cookie(response, session_id)

    cookies = [c for c in response.raw_headers if b"quiz_session_id" in c[1]]
    assert cookies  # should not be empty
