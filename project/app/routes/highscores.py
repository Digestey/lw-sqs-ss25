# app/routes/highscores.py

from typing import List
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database.database import get_highscores
from services.pokemon_service import fetch_pokemon
from util.logger import get_logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}

class HighscoreResponse(BaseModel):
    username: str
    score: int


@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores(request: Request):
    highscores = get_highscores()
    if highscores is None:
        # there are no highscores yet.
        return JSONResponse(content="{}")
    return highscores
