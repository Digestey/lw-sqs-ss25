import pytest
from types import SimpleNamespace
from app.services import pokemon_service


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
