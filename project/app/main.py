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
from app.services.database_service import is_database_healthy

# Initialization of the application

load_dotenv()
logging.basicConfig()
logger = get_logger(name="DexQuiz", debug=True, level=logging.DEBUG)

sessions = {}
app = FastAPI()
cache_dir = os.getenv("POKEMON_CACHE", default="./cache")
host_ip = os.getenv("HOST_IP", "127.0.0.1")

pb.cache.set_cache()

logger.info("Welcome to the DexQuiz Application")

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
    if is_database_healthy(
        host=host_ip,
        user=os.getenv("MYSQL_USER", "trainer"),
        password=os.getenv("MYSQL_PASSWORD", "pokeballs"),
        database=os.getenv("MYSQL_DATABASE", "pokedb")):
        logger.info("Database is healthy.")
    else:
        logger.warning("Database is NOT reachable.")
    if os.getenv("USE_TEST_POKEMON") == "1":
        logger.info("USING TEST DATA.")
    import uvicorn
    uvicorn.run(app, host=host_ip, port=8000)
