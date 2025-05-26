"""
Main entry point for the DexQuiz Application
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pokebase as pb
from dotenv import load_dotenv
from routes import frontend, highscores, users
from util.logger import get_logger

# Initialization of the application

load_dotenv()
logging.basicConfig()
logger = get_logger(name="DexQuiz", debug=True, level=logging.DEBUG)

sessions = {}
app = FastAPI()
cache_dir = os.getenv("POKEMON_CACHE", default="./cache")

pb.cache.set_cache()

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
app.include_router(highscores.router)
app.include_router(users.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
