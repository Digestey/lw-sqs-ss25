"""
Module highscores: Contains all backend routes that are highscore-related.
"""
from typing import List
from fastapi import APIRouter, Cookie, HTTPException, Request, Depends
import mysql

from app.services.database_service import get_highscores, add_highscore, get_top_highscores, get_connection
from app.services.auth_service import get_user_from_token, oauth2_scheme
from app.util.logger import get_logger
from app.models.highscore_response import HighscoreResponse
from app.models.user_in_db import UserInDb

router = APIRouter()
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}


def get_token_from_cookie(access_token: str | None = Cookie(default=None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token

def get_current_user_from_cookie(token: str = Depends(get_token_from_cookie)) -> UserInDb:
    db_conn = get_connection()
    try:
        user = get_user_from_token(token, db_conn)
        return user
    finally:
        db_conn.close()

@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores(user: UserInDb = Depends(get_current_user_from_cookie)):
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
        highscores = get_highscores(db_conn)
        return highscores
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        db_conn.close()


@router.get("/api/highscore/{top}", response_model=List[HighscoreResponse])
async def get_top_highscores_api(
    top: int,
    user: UserInDb = Depends(get_current_user_from_cookie)
):
    """
    Returns the top N highscores. Requires login.

    Args:
        top (int): Number of top scores to return.
        user (UserInDb): The authenticated user (not used, but required for access).

    Returns:
        List[HighscoreResponse]: The top N highscore entries.
    """
    db_conn = None
    try:
        db_conn = get_connection()
        highscores = get_top_highscores(db_conn, top)
        return highscores
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if db_conn:
            db_conn.close()


@router.post("/api/highscore")
async def post_highscore(request: Request, user: UserInDb = Depends(get_current_user_from_cookie)):
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
    db_conn = None
    try:
        db_conn = get_connection()
        highscore_data = add_highscore(db_conn, user.username, obj['score'])
        return highscore_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail="Internal server error") from e
    finally:
        db_conn.close()
