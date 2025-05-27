"""
Module pokemon_service:

Connects to PokeAPI via PokeBase Wrapper.
"""
import os
import random
import pokebase as pb
from dotenv import load_dotenv

from app.util.logger import Logger
from app.QuizInfo import QuizInfo

load_dotenv()
pb.cache.set_cache(os.getenv("POKEMON_CACHE"))


def english_dex_entry(pokemon):
    """Extracts English Pokedex entry from pokemon object returned by the API

    Args:
        pokemon (pokemon): Pokemon

    Returns:
        str: Random English PokeDex Entry.
    """
    english_entries = [
        entry for entry in pokemon.species.flavor_text_entries if entry.language.name == "en"]

    # If there are English entries, return a random one
    if english_entries:
        random_entry = random.choice(english_entries)
        return random_entry.flavor_text
    else:
        return "No English entry found."


def fetch_pokemon(logger: Logger):
    """Fetches a random Pokemon from the PokeAPI.

    Args:
        logger (Logger): Logger

    Returns:
        pokemon: A random Pokemon object.
    """
    pokemonid = random.randrange(1, 1025, 1)
    current_pokemon = pb.pokemon(pokemonid)  # Fetch Pokémon data

    # in production, this would be hidden. but me being an idiot, i keep it here
    print(f"Name\t\t\t\t: {current_pokemon.name}")
    print(f"Id\t\t\t\t\t: {current_pokemon.id}")
    print(f"Height\t\t\t\t: {current_pokemon.height}")
    print(f"Weight\t\t\t\t: {current_pokemon.weight}")
    print(
        f"{current_pokemon.stats[0].stat}\t\t\t\t: {current_pokemon.stats[0].base_stat}")
    print(
        f"{current_pokemon.stats[1].stat}\t\t\t\t: {current_pokemon.stats[1].base_stat}")
    print(
        f"{current_pokemon.stats[2].stat}\t\t\t\t: {current_pokemon.stats[2].base_stat}")
    print(
        f"{current_pokemon.stats[3].stat}\t\t\t: {current_pokemon.stats[3].base_stat}")
    print(
        f"{current_pokemon.stats[4].stat}\t\t\t: {current_pokemon.stats[4].base_stat}")
    print(
        f"{current_pokemon.stats[5].stat}\t\t\t\t: {current_pokemon.stats[5].base_stat}")
    print(f"Type:\t\t\t\t: {current_pokemon.types[0].type}")

    if len(current_pokemon.types) != 1:
        # Debugging info
        logger.debug(f"Secondary Type:\t\t\t: {current_pokemon.types[1].type}")

    entry = english_dex_entry(current_pokemon)
    logger.debug(f"Dex-Entry:\t\t\t: {entry}")  # Debugging info
    # Collecting Pokémon Information
    stats = {stat.stat.name.capitalize(
    ): stat.base_stat for stat in current_pokemon.stats}
    types = [type.type.name.capitalize() for type in current_pokemon.types]
    entry = english_dex_entry(current_pokemon)
    quizmon = QuizInfo(current_pokemon.name, current_pokemon.id,
                       current_pokemon.height, current_pokemon.weight, stats, types, entry)
    print(vars(quizmon))
    print(quizmon.__dict__)
    return quizmon
