"""Froentend integration tests"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app  # Adjust to your actual FastAPI app entrypoint
from app.models.quiz_info import QuizInfo

client = TestClient(app)

def test_homepage():
    """Check if template is returned when accessing"""
    response = client.get("/")
    assert response.status_code == 200
    assert "DexQuiz" in response.text
    
def test_login_frontend():
    """Check if login template is returned"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text
    
def test_register_frontend():
    """check if register template is returned"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "register" in response.text
    
def test_get_quiz_generates_new_session_and_sets_state(client):
    """Test the quiz page. This took AGES. (and lots of chatgpt-ing)"""
    fake_pokemon = QuizInfo(
        name="bulbasaur",
        pokemon_id=1,
        height=7,
        weight=69,
        stats={
            "hp": 45,
            "attack": 49,
            "defense": 81,
            "special_attack": 60,
            "special_defense": 60,
            "speed": 80
        },
        types=["Grass", "Poison"],
        entry="THIS IS A TEST ENTRY: A strange seed was planted on its back at birth."
    )

    with patch("app.routes.quiz.get_state", return_value=None), \
         patch("app.routes.quiz.set_state") as mock_set_state, \
         patch("app.routes.quiz.fetch_pokemon", return_value=fake_pokemon):

        response = client.get("/quiz")
        assert response.status_code == 200
        text = response.text.lower()

        # Check if the Pokémon types are rendered
        assert "type_icons/grass.png" in text or "grass" in text
        assert "type_icons/poison.png" in text or "poison" in text

        # Check height and weight
        assert "height: 7" in text or "7" in text
        assert "weight: 69" in text or "69" in text

        # Check the dex entry snippet
        assert "a strange seed was planted on its back" in text

        # Check that all stat values appear somewhere in the response text
        for stat_name, stat_value in fake_pokemon.stats.items():
            assert str(stat_value) in text
