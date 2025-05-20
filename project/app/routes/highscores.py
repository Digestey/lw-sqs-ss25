# app/routes/highscores.py

from typing import List
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import mysql
import datetime
from pydantic import BaseModel

from services.database_service import get_highscores, add_highscore, get_top_highscores
from services.pokemon_service import fetch_pokemon
from util.logger import get_logger

router = APIRouter()
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}

class HighscoreResponse(BaseModel):
    username: str
    score: int
    achieved_at: datetime.datetime

class HighscoreRequest(BaseModel):
    username: str
    score: int

@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores():
    try:    
        highscores = get_highscores() 
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e
    return highscores

@router.get("/api/highscore/{top}", response_model=List[HighscoreResponse])
async def get_highscore_by_id(top: int):
    try:
        highscore = get_top_highscores(top)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e
    return highscore

@router.post("/api/highscore", response_model=List[HighscoreResponse])
async def post_highscore(request: Request):
    obj = await request.json()
    try:
        highscore_data = add_highscore(obj['username'], obj['score'])
        
        # Here, `highscore_data` should include the `achieved_at` value
        # from the result returned by the `add_highscore` function.
        
        # Example: HighscoreResponse(username=..., score=..., achieved_at=...)
        # Or you can return it directly if the function is set to return that model.
        
        return highscore_data  # Ensure that the `add_highscore` returns data with `achieved_at`
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e