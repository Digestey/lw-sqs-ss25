"""
pokemon_service.py

This module provides functionality to fetch, format, and log Pokémon data for quiz-related use
within the application. It leverages the PokéBase API to retrieve Pokémon stats, types, and
Pokédex entries. It also includes a fallback mechanism for testing scenarios.

Main Features:
- Fetches a random Pokémon with complete info for quiz generation.
- Extracts and formats stats, types, and English Pokédex entries.
- Logs useful debug information via a custom logger.
- Supports test mode via the USE_TEST_POKEMON environment variable.

Environment Variables:
- USE_TEST_POKEMON: If set to "1", a hardcoded test Pokémon (Bulbasaur) will be returned.
- POKEMON_CACHE: Path for PokéBase API response caching (used by pokebase).
"""
import os
import re
import secrets
import requests
from fastapi import HTTPException
import pokebase as pb
from dotenv import load_dotenv
from app.util.logger import Logger
from app.models.quiz_info import QuizInfo

load_dotenv()
pb.cache.set_cache(os.getenv("POKEMON_CACHE"))


def get_random_pokemon_id(min_id=1, max_id=1025):
    """Generate a random Pokémon ID within the National Dex range.

    Args:
        min_id (int, optional): Minimum Pokémon ID. Defaults to 1.
        max_id (int, optional): Maximum Pokémon ID. Defaults to 1025.

    Returns:
        int: A randomly selected Pokémon ID.
    """
    return min_id + secrets.randbelow(max_id - min_id + 1)


def get_english_dex_entry(species, name):
    """Retrieve a random English-language Pokédex entry from a Pokémon species.

    Args:
        species (pokebase.Model): A species object returned by PokeBase.

    Returns:
        str: A random English Pokédex flavor text, or a fallback message if none are found.
    """
    english_entries = [
        entry.flavor_text for entry in species.flavor_text_entries
        if entry.language.name == "en"
    ]
    entry = secrets.choice(english_entries) if english_entries else "No English entry found."
    pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
    entry = pattern.sub("[Pokémon]", entry)
    return entry


def extract_stats(stats_data):
    """Convert raw base stat objects into a dictionary with readable names.

    Args:
        stats_data (List[pokebase.Stat]): A list of stat objects from PokeBase.

    Returns:
        dict: A dictionary mapping stat names (capitalized) to base stat values.
    """
    return {
        stat.stat.name.capitalize(): stat.base_stat
        for stat in stats_data
    }


def extract_types(types_data):
    """Extract and capitalize the Pokémon's types.

    Args:
        types_data (List[pokebase.Type]): A list of type slot objects from PokeBase.

    Returns:
        List[str]: A list of type names (capitalized).
    """
    return [t.type.name.capitalize() for t in types_data]


def log_pokemon_details(logger: Logger, pokemon):
    """Log details of a Pokémon including name, ID, stats, and types.

    Args:
        logger (Logger): Custom application logger.
        pokemon (pokebase.Pokemon): A Pokémon object returned by PokeBase.
    """
    logger.info(msg=f"Name: {pokemon.name}")
    logger.debug(f"Id: {pokemon.id}")
    logger.debug(f"Height: {pokemon.height}")
    logger.debug(f"Weight: {pokemon.weight}")
    for stat in pokemon.stats:
        logger.debug(f"{stat.stat.name.capitalize()}: {stat.base_stat}")
    logger.debug("Types: " + ", ".join(t.type.name for t in pokemon.types))


def get_test_pokemon() -> QuizInfo:
    """Returns a test pokemon during testing. Not for production use. only testing.

    Returns:
        QuizInfo: Object filled with fixed testing data.
    """
    stats_dict = {
        "Hp": 45,
        "Attack": 49,
        "Defense": 81,
        "Special-attack": 60,
        "Special-defense": 60,
        "Speed": 80
    }
    return QuizInfo(
        name="bulbasaur",
        pokemon_id=1,
        height=7,
        weight=69,
        stats=stats_dict,
        types=["Grass", "Poison"],
        entry="THIS IS A TEST ENTRY: A strange seed was planted on its back at birth."
    )


def fetch_pokemon(logger: Logger) -> QuizInfo:
    """Fetch a random Pokémon and return a QuizInfo object for use in quizzes.

    If the environment variable USE_TEST_POKEMON is set to "1", test data is returned
    instead of querying the PokeBase API.

    Args:
        logger (Logger): Custom application logger for detailed output.

    Returns:
        QuizInfo: A structured object containing key quiz data about a Pokémon.

    Raises:
        HTTPException: If the external PokéAPI is unreachable or returns invalid data.
    """
    if os.getenv("USE_TEST_POKEMON") == "1":
        return get_test_pokemon()
    try:
        pokemon_id = get_random_pokemon_id()
        pokemon = pb.pokemon(pokemon_id)

        log_pokemon_details(logger, pokemon)

        stats = extract_stats(pokemon.stats)
        types = extract_types(pokemon.types)
        entry = get_english_dex_entry(pokemon.species, pokemon.name)

        return QuizInfo(
            name=pokemon.name,
            pokemon_id=pokemon.id,
            height=pokemon.height,
            weight=pokemon.weight,
            stats=stats,
            types=types,
            entry=entry
        )

    except (requests.exceptions.RequestException, AttributeError, KeyError) as e:
        logger.error(f"Failed to fetch Pokémon data: {e}")
        raise HTTPException(
            status_code=503, detail="External Pokémon API is unavailable.") from e
