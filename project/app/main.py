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
from app.routes import frontend, highscores, users
from app.util.logger import get_logger

# Initialization of the application
print("Starting DexQuiz application...")
print(os.getenv("USE_TEST_POKEMON"))

load_dotenv()
logging.basicConfig()
logger = get_logger(name="DexQuiz", debug=True, level=logging.DEBUG)

sessions = {}
app = FastAPI()
cache_dir = os.getenv("POKEMON_CACHE", default="./cache")
host_ip = os.getenv("HOST_IP", "127.0.0.1")

pb.cache.set_cache()



# print(f"{dir(pb.cache.API_CACHE)}")

# Mount the required directories for the webpage

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)
app.mount(
    "/images",
    StaticFiles(directory=BASE_DIR / "images"),
    name="images",
)

app.include_router(frontend.router)
app.include_router(highscores.router)
app.include_router(users.router)


if __name__ == "__main__":
    if os.getenv("USE_TEST_POKEMON") == "1":
        print("Using testing pokemon...")
    import uvicorn
    uvicorn.run(app, host=host_ip, port=8000)
