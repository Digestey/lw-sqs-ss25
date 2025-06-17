"""
Module highscores: Contains all backend routes that are highscore-related.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Request, Depends
import mysql

from app.services.database_service import get_highscores, add_highscore, get_top_highscores, get_connection
from app.services.auth_service import get_user_from_token, oauth2_scheme
from app.util.logger import get_logger
from app.models.highscore_response import HighscoreResponse

router = APIRouter()
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}


@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores(token: str = Depends(oauth2_scheme)):
    """_summary_

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    db_conn = None
    try:
        db_conn = get_connection()
        username = get_user_from_token(token, db_conn)
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid access token")
        highscores = get_highscores(db_conn)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if db_conn:
            db_conn.close()
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
    db_conn = None
    try:
        db_conn = get_connection()
        highscores = get_top_highscores(db_conn, top)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if db_conn:
            db_conn.close()
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
    db_conn = None
    obj = await request.json()
    try:
        db_conn = get_connection()
        user = get_user_from_token(token, db_conn)
        highscore_data = add_highscore(db_conn, user.username, obj['score'])
        return highscore_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail="Internal server error") from e
    finally:
        if db_conn:
            db_conn.close()
