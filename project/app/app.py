# app.py
import random
import os
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import pokebase as pb
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import re


# Initialization of the application

load_dotenv()

sessions = {}
app = FastAPI()
templates = Jinja2Templates(directory="templates")

pb.cache.set_cache(os.getenv("POKEMON_CACHE"))

# print(f"{dir(pb.cache.API_CACHE)}")

# Mount the required directories for the webpage

app.mount(
    "/static",
    StaticFiles(directory=Path("static/")),
    name="static",
)
app.mount(
    "/images",
    StaticFiles(directory=Path("images/")),
    name="images"
)

def english_dex_entry(pokemon):
    english_entries = [
        entry for entry in pokemon.species.flavor_text_entries if entry.language.name == "en"]

    # If there are English entries, return a random one
    if english_entries:
        random_entry = random.choice(english_entries).flavor_text
        result = re.sub(re.escape(pokemon.name), "The Pokemon", random_entry, flags=re.IGNORECASE)
        return result
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

# Route for the homepage


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Load home template
    return templates.TemplateResponse("index.html", {"request": request, "user_name": "John Doe"})


@app.post("/submit", response_class=HTMLResponse)
async def submit(request: Request, name: str = Form(...)):
    return templates.TemplateResponse("index.html", {"request": request, "user_name": name})


@app.get("/quiz")
async def get_quiz(request: Request):
    session_id = request.client.host  # Use client IP as a simple session identifier
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon()

    pokemon_info = sessions[session_id]

    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "message": "",
            "reload": False,
            "pokemon": pokemon_info
        }
    )


@app.post("/quiz")
async def post_quiz(request: Request, guess: str = Form(...)):
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon()

    correct_answer = sessions[session_id]["name"].lower()
    guess = guess.strip().lower()

    if guess == correct_answer:
        del sessions[session_id]  # Reset session on correct guess
        return JSONResponse(content={"correct": True, "message": "Ding Ding Ding! We have a winner!"})

    # Reveal a new hint for incorrect guesses
    hint_index = sessions[session_id].get("hint_index", 0)
    hints = sessions[session_id].get("hints", [])  # List of hints to reveal
    hint_index = min(hint_index + 1, len(hints))  # Increment hint index but don't exceed max hints
    sessions[session_id]["hint_index"] = hint_index

    return JSONResponse(content={"correct": False, "message": "That is incorrect. Another hint has been added to the entry", "hint": hints[:hint_index]})

def get_hint(wrong_guesses):
    """Determine the hints that are to be displayed

    Args:
        wrong_guesses (number): Number of incorrect guesses

    Returns:
        _type_: _description_
    """
    hints = [
        "height",
        "weight",
        "species",
        "types",
        "secondary_type",
        "dex_entry",
        "base_hp",
        "base_attack",
        "base_defense",
        "base_special_attack",
        "base_special_defense",
        "base_speed",
        "abilities"
    ]

    # Ensure the wrong_guesses do not go beyond the available hints
    if wrong_guesses <= len(hints):
        return hints[wrong_guesses - 1]
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
