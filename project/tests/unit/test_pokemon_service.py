import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from app.services import pokemon_service
from app.models.quiz_info import QuizInfo
from app.util.logger import Logger


def test_get_random_pokemon_id_within_range():
    for _ in range(100):
        pid = pokemon_service.get_random_pokemon_id(1, 10)
        assert 1 <= pid <= 10


def test_get_english_dex_entry_returns_entry():
    mock_species = SimpleNamespace(flavor_text_entries=[
        SimpleNamespace(language=SimpleNamespace(name="en"), flavor_text="A wild Pokémon."),
        SimpleNamespace(language=SimpleNamespace(name="jp"), flavor_text="ワイルドポケモン")
    ])
    result = pokemon_service.get_english_dex_entry(mock_species)
    assert result == "A wild Pokémon."


def test_get_english_dex_entry_empty():
    mock_species = SimpleNamespace(flavor_text_entries=[
        SimpleNamespace(language=SimpleNamespace(name="jp"), flavor_text="ワイルドポケモン")
    ])
    result = pokemon_service.get_english_dex_entry(mock_species)
    assert result == "No English entry found."


def test_extract_stats():
    mock_stats = [
        SimpleNamespace(stat=SimpleNamespace(name="hp"), base_stat=45),
        SimpleNamespace(stat=SimpleNamespace(name="attack"), base_stat=60)
    ]
    result = pokemon_service.extract_stats(mock_stats)
    assert result == {"Hp": 45, "Attack": 60}


def test_extract_types():
    mock_types = [
        SimpleNamespace(type=SimpleNamespace(name="grass")),
        SimpleNamespace(type=SimpleNamespace(name="poison"))
    ]
    result = pokemon_service.extract_types(mock_types)
    assert result == ["Grass", "Poison"]




@patch("app.services.pokemon_service.pb.pokemon")
@patch("app.services.pokemon_service.get_random_pokemon_id", return_value=1)
def test_fetch_pokemon(mock_get_random_id, mock_pb_pokemon):
    # Mocking pokemon object
    mock_pokemon = MagicMock()
    mock_pokemon.name = "bulbasaur"
    mock_pokemon.id = 1
    mock_pokemon.height = 7
    mock_pokemon.weight = 69

    # Mock stats
    mock_stat = MagicMock()
    mock_stat.stat.name = "hp"
    mock_stat.base_stat = 45
    mock_pokemon.stats = [mock_stat]

    # Mock types
    mock_type = MagicMock()
    mock_type.type.name = "grass"
    mock_pokemon.types = [mock_type]

    # Mock species and dex entry
    mock_species = MagicMock()
    flavor_entry = MagicMock()
    flavor_entry.language.name = "en"
    flavor_entry.flavor_text = "A strange seed was planted on its back at birth."
    mock_species.flavor_text_entries = [flavor_entry]
    mock_pokemon.species = mock_species

    mock_pb_pokemon.return_value = mock_pokemon

    # Run function
    logger = MagicMock(spec=Logger)
    result = pokemon_service.fetch_pokemon(logger)

    # Assertions
    assert isinstance(result, QuizInfo)
    assert result.name == "bulbasaur"
    assert result.types == ["Grass"]
    assert result.stats == {"Hp": 45}
    assert "seed" in result.entry.lower()