# pokemon_api.py
import os
import random
import pokebase as pb
from dotenv import load_dotenv

from util.logger import Logger
from QuizInfo import QuizInfo

load_dotenv()
pb.cache.set_cache(os.getenv("POKEMON_CACHE"))


def english_dex_entry(pokemon):
    english_entries = [
        entry for entry in pokemon.species.flavor_text_entries if entry.language.name == "en"]

    # If there are English entries, return a random one
    if english_entries:
        random_entry = random.choice(english_entries)
        return random_entry.flavor_text
    else:
        return "No English entry found."


def fetch_pokemon(logger: Logger):
    pokemonid = random.randrange(1, 1025, 1)
    current_pokemon = pb.pokemon(pokemonid)  # Fetch Pokémon data

    # Debug output for generated Pokémon
    logger.debug("===================GENERATED POKEMON      INFORMATION=============================================================================================================================================================================")
    logger.debug(f"Name\t\t\t\t: {current_pokemon.name}")
    logger.debug(f"Id\t\t\t\t\t: {current_pokemon.id}")
    logger.debug(f"Height\t\t\t\t: {current_pokemon.height}")
    logger.debug(f"Weight\t\t\t\t: {current_pokemon.weight}")
    logger.debug(
        f"{current_pokemon.stats[0].stat}\t\t\t\t: {current_pokemon.stats[0].base_stat}")
    logger.debug(
        f"{current_pokemon.stats[1].stat}\t\t\t\t: {current_pokemon.stats[1].base_stat}")
    logger.debug(
        f"{current_pokemon.stats[2].stat}\t\t\t\t: {current_pokemon.stats[2].base_stat}")
    logger.debug(
        f"{current_pokemon.stats[3].stat}\t\t\t: {current_pokemon.stats[3].base_stat}")
    logger.debug(
        f"{current_pokemon.stats[4].stat}\t\t\t: {current_pokemon.stats[4].base_stat}")
    logger.debug(
        f"{current_pokemon.stats[5].stat}\t\t\t\t: {current_pokemon.stats[5].base_stat}")
    logger.debug(f"Type:\t\t\t\t: {current_pokemon.types[0].type}")

    if len(current_pokemon.types) != 1:
        # Debugging info
        logger.debug(f"Secondary Type:\t\t\t: {current_pokemon.types[1].type}")

    entry = english_dex_entry(current_pokemon)
    print(f"Dex-Entry:\t\t\t: {entry}")  # Debugging info
    # Collecting Pokémon Information
    stats = {stat.stat.name.capitalize(
    ): stat.base_stat for stat in current_pokemon.stats}
    types = [type.type.name.capitalize() for type in current_pokemon.types]
    entry = english_dex_entry(current_pokemon)
    quizmon = QuizInfo(current_pokemon.name, current_pokemon.id,
                       current_pokemon.height, current_pokemon.weight, stats, types, entry)

    return quizmon
