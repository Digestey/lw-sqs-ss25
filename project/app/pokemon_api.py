# pokemon_api.py
import os
import random
import pokebase as pb
from dotenv import load_dotenv

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


def fetch_pokemon():
    pokemonid = random.randrange(1, 1025, 1)
    current_pokemon = pb.pokemon(pokemonid)  # Fetch Pokémon data

    # Here be debug print
    print("===================GENERATED POKEMON INFORMATION=============================================================================================================================================================================")
    print(f"Name\t\t\t\t: {current_pokemon.name}")  # Debugging info
    print(f"Id\t\t\t\t\t: {current_pokemon.id}")
    print(f"Height\t\t\t\t: {current_pokemon.height}")
    print(f"Weight\t\t\t\t: {current_pokemon.weight}")
    # Debugging info
    print(
        f"{current_pokemon.stats[0].stat}\t\t\t\t: {current_pokemon.stats[0].base_stat}")
    # Debugging info
    print(
        f"{current_pokemon.stats[1].stat}\t\t\t\t: {current_pokemon.stats[1].base_stat}")
    # Debugging info
    print(
        f"{current_pokemon.stats[2].stat}\t\t\t\t: {current_pokemon.stats[2].base_stat}")
    # Debugging info
    print(
        f"{current_pokemon.stats[3].stat}\t\t\t: {current_pokemon.stats[3].base_stat}")
    # Debugging info
    print(
        f"{current_pokemon.stats[4].stat}\t\t\t: {current_pokemon.stats[4].base_stat}")
    # Debugging info
    print(
        f"{current_pokemon.stats[5].stat}\t\t\t\t: {current_pokemon.stats[5].base_stat}")
    print(f"Type:\t\t\t\t: {current_pokemon.types[0].type}")  # Debugging info
    if len(current_pokemon.types) != 1:
        # Debugging info
        print(f"Secondary Type:\t\t\t: {current_pokemon.types[1].type}")
    entry = english_dex_entry(current_pokemon)
    print(f"Dex-Entry:\t\t\t: {entry}")  # Debugging info
    # Collecting Pokémon Information
    pokemon_info = {
        "name": current_pokemon.name,
        "id": current_pokemon.id,
        "height": current_pokemon.height,
        "weight": current_pokemon.weight,
        "stats": {stat.stat.name.capitalize(): stat.base_stat for stat in current_pokemon.stats},
        "types": [type.type.name.capitalize() for type in current_pokemon.types],
        "dex_entry": english_dex_entry(current_pokemon)
    }

    return pokemon_info