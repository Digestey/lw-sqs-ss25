# app.py
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
import pokebase as pb
from dotenv import load_dotenv
from routes import frontend
from services.pokemon_service import fetch_pokemon
from util.logger import get_logger

# Initialization of the application

load_dotenv()
logging.basicConfig()
logger = get_logger(name="DexQuiz", debug=True, level=logging.DEBUG)

sessions = {}
app = FastAPI()

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

app.include_router(frontend.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
