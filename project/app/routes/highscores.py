"""
Module highscores: Contains all backend routes that are highscore-related.
"""
import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Request, Depends
import mysql
from pydantic import BaseModel

from app.services.database_service import get_highscores, add_highscore, get_top_highscores
from app.services.auth_service import get_user_from_token, oauth2_scheme
from app.util.logger import get_logger

router = APIRouter()
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}


class HighscoreResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    username: str
    score: int
    achieved_at: datetime.datetime


class HighscoreRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    username: str
    score: int


@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores():
    """_summary_

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        highscores = get_highscores()
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return highscores


@router.get("/api/highscore/{top}", response_model=List[HighscoreResponse])
async def get_top_highscores_api(top: int, token: str = Depends(oauth2_scheme)):
    """_summary_

    Args:
        top (int): _description_
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        highscores = get_top_highscores(top)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return highscores


@router.post("/api/highscore")
async def post_highscore(request: Request, token: str = Depends(oauth2_scheme)):
    """_summary_

    Args:
        request (Request): _description_
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    obj = await request.json()
    try:
        username = get_user_from_token(token)
        highscore_data = add_highscore(username, obj['score'])
        return highscore_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail="Internal server error") from e
