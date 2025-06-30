"""Pokemon Service Unit tests"""
import os
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from app.services import pokemon_service
from app.models.quiz_info import QuizInfo
from app.util.logger import Logger


def test_get_random_pokemon_id_within_range():
    """Test if get random pokemon works"""
    for _ in range(100):
        pid = pokemon_service.get_random_pokemon_id(1, 10)
        assert 1 <= pid <= 10


def test_get_english_dex_entry_returns_entry():
    """Test if it really does only extract english pokedex entries"""
    mock_species = SimpleNamespace(flavor_text_entries=[
        SimpleNamespace(language=SimpleNamespace(name="en"),
                        flavor_text="A wild Pokémon."),
        SimpleNamespace(language=SimpleNamespace(
            name="jp"), flavor_text="ワイルドポケモン")
    ])
    result = pokemon_service.get_english_dex_entry(mock_species)
    assert result == "A wild Pokémon."


def test_get_english_dex_entry_empty():
    """Check if it tells an error if no entry was found"""
    mock_species = SimpleNamespace(flavor_text_entries=[
        SimpleNamespace(language=SimpleNamespace(
            name="jp"), flavor_text="ワイルドポケモン")
    ])
    result = pokemon_service.get_english_dex_entry(mock_species)
    assert result == "No English entry found."


def test_extract_stats():
    """Check if the stats are extracted correctly"""
    mock_stats = [
        SimpleNamespace(stat=SimpleNamespace(name="hp"), base_stat=45),
        SimpleNamespace(stat=SimpleNamespace(name="attack"), base_stat=60)
    ]
    result = pokemon_service.extract_stats(mock_stats)
    assert result == {"Hp": 45, "Attack": 60}


def test_extract_types():
    """Check if the types are extracted correctly"""
    mock_types = [
        SimpleNamespace(type=SimpleNamespace(name="grass")),
        SimpleNamespace(type=SimpleNamespace(name="poison"))
    ]
    result = pokemon_service.extract_types(mock_types)
    assert result == ["Grass", "Poison"]


@patch("app.services.pokemon_service.pb.pokemon")
@patch("app.services.pokemon_service.get_random_pokemon_id", return_value=1)
def test_fetch_pokemon(mock_get_random_id, mock_pb_pokemon):
    """Testing fetch_pokemon by mocking the API"""
    logger = MagicMock(spec=Logger)
    result = pokemon_service.fetch_pokemon(logger)

    # Assertions
    assert isinstance(result, QuizInfo)
    assert result.name == "bulbasaur"
    assert result.types == ["Grass", "Poison"]
    assert result.stats == {'Hp': 45, 'Attack': 49, 'Defense': 81,
                            'Special-attack': 60, 'Special-defense': 60, 'Speed': 80}

    assert "seed" in result.entry.lower()


# Mock the pokebase.pokemon call inside fetch_pokemon
@patch("pokebase.pokemon")
def test_fetch_pokemon_with_use_test_pokemon_env(mock_pb_pokemon):
    """Testing fetch_pokemon by using the env"""
    # Lets mock everything that the pokebase does (thanks chatgpt)
    logger = MagicMock(spec=Logger)
    mock_pokemon_instance = MagicMock()
    mock_pokemon_instance.name = "charmander"
    mock_pokemon_instance.id = 4
    mock_pokemon_instance.height = 6
    mock_pokemon_instance.weight = 85
    mock_pokemon_instance.stats = [
        MagicMock(stat=MagicMock(name="hp"), base_stat=39),
        MagicMock(stat=MagicMock(name="attack"), base_stat=52),
    ]
    mock_type = MagicMock()
    mock_type.type.name = "Fire"
    mock_pokemon_instance.types = [mock_type]
    mock_pokemon_instance.species = MagicMock()

    language_mock = MagicMock()
    language_mock.name = "en"

    entry_mock = MagicMock()
    entry_mock.flavor_text = "A fiery lizard Pokémon."
    entry_mock.language = language_mock

    mock_pokemon_instance.species.flavor_text_entries = [entry_mock]
    mock_pb_pokemon.return_value = mock_pokemon_instance
    os.environ["USE_TEST_POKEMON"] = "1"

    # Call fetch_pokemon, check if its the test value
    result = pokemon_service.fetch_pokemon(logger)
    assert isinstance(result, QuizInfo)
    assert result.name == "bulbasaur"
    assert result.pokemon_id == 1
    assert "THIS IS A TEST ENTRY" in result.entry
    assert os.environ["USE_TEST_POKEMON"] == "1"

    # Now set USE_TEST_POKEMON to "0" and call fetch_pokemon again
    os.environ["USE_TEST_POKEMON"] = "0"
    result = pokemon_service.fetch_pokemon(logger)

    # Now it should be the mock.
    assert isinstance(result, QuizInfo)
    assert result.name == "charmander"
    assert result.pokemon_id == 4
    assert "fiery lizard" in result.entry.lower()

    # set it back for further testing

    os.environ["USE_TEST_POKEMON"] = "1"
    assert os.environ["USE_TEST_POKEMON"] == "1"
