"""
pokemon_service.py

Provides functionality to fetch and format Pokémon data using PokeBase.
"""

import os
import random
import pokebase as pb
from dotenv import load_dotenv
from app.util.logger import Logger
from app.models.quiz_info import QuizInfo

load_dotenv()
pb.cache.set_cache(os.getenv("POKEMON_CACHE"))


def get_random_pokemon_id(min_id=1, max_id=1025):
    return random.randint(min_id, max_id)


def get_english_dex_entry(species):
    """Returns a random English Pokédex entry."""
    english_entries = [
        entry.flavor_text for entry in species.flavor_text_entries
        if entry.language.name == "en"
    ]
    return random.choice(english_entries) if english_entries else "No English entry found."


def extract_stats(stats_data):
    """Transforms raw stats into a readable dict."""
    return {
        stat.stat.name.capitalize(): stat.base_stat
        for stat in stats_data
    }


def extract_types(types_data):
    """Extracts and formats type names."""
    return [t.type.name.capitalize() for t in types_data]


def log_pokemon_details(logger: Logger, pokemon):
    logger.log(msg=f"Name: {pokemon.name}")
    logger.debug(f"Id: {pokemon.id}")
    logger.debug(f"Height: {pokemon.height}")
    logger.debug(f"Weight: {pokemon.weight}")
    for stat in pokemon.stats:
        logger.debug(f"{stat.stat.name.capitalize()}: {stat.base_stat}")
    logger.debug("Types: " + ", ".join(t.type.name for t in pokemon.types))


def fetch_pokemon(logger: Logger) -> QuizInfo:
    """Fetches a random Pokémon and returns a QuizInfo object."""
    pokemon_id = get_random_pokemon_id()
    pokemon = pb.pokemon(pokemon_id)

    log_pokemon_details(logger, pokemon)

    stats = extract_stats(pokemon.stats)
    types = extract_types(pokemon.types)
    entry = get_english_dex_entry(pokemon.species)

    return QuizInfo(
        name=pokemon.name,
        id=pokemon.id,
        height=pokemon.height,
        weight=pokemon.weight,
        stats=stats,
        types=types,
        dex_entry=entry
    )
