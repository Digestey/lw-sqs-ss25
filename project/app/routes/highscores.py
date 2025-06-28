"""
Module highscores: Contains all backend routes that are highscore-related.
"""
import json
from typing import List
from fastapi import APIRouter, Cookie, HTTPException, Request, Depends
import mysql

from app.services.database_service import get_highscores, add_highscore, get_top_highscores, get_connection
from app.services.auth_service import get_user_from_token
from app.services.redis_service import get_redis_client
from app.util.logger import get_logger
from app.models.highscore_response import HighscoreResponse
from app.models.user_in_db import UserInDb


router = APIRouter()
logger = get_logger("Highscore")

# In-memory session store (basic)
sessions = {}


def get_token_from_cookie(access_token: str | None = Cookie(default=None)):
    """Retrieves the JWT access token from cookies.

    Raises:
        HTTPException: If the token is not present in the cookies.

    Returns:
        str: The JWT access token.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token


def get_current_user_from_cookie(token: str = Depends(get_token_from_cookie)) -> UserInDb:
    """Retrieves the current user based on the token stored in cookies.

    Args:
        token (str): JWT token obtained from cookies.

    Returns:
        UserInDb: The user associated with the token.

    Raises:
        HTTPException: If token is invalid or user cannot be found.
    """
    db_conn = get_connection()
    try:
        user = get_user_from_token(token, db_conn)
        return user
    finally:
        if db_conn:
            db_conn.close()


@router.get("/api/highscores", response_model=List[HighscoreResponse])
async def get_all_highscores(user: UserInDb = Depends(get_current_user_from_cookie)):
    """Returns all highscores in the database.

    Requires user to be authenticated via a JWT token in cookies.

    Args:
        user (UserInDb): The authenticated user.

    Returns:
        List[HighscoreResponse]: A list of all highscores.

    Raises:
        HTTPException: 404 if highscores are not found.
        HTTPException: 500 if a database error occurs.
    """
    db_conn = None
    try:
        db_conn = get_connection()
        highscores = get_highscores(db_conn)
        return highscores
    except ValueError as valueerr:
        raise HTTPException(status_code=404, detail=str(valueerr)) from valueerr
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
    finally:
        if db_conn:
            db_conn.close()


@router.get("/api/highscore/{top}", response_model=List[HighscoreResponse])
async def get_top_highscores_api(
    top: int,
    user: UserInDb = Depends(get_current_user_from_cookie)
):
    """"Returns the top N highscores. Requires authentication.

    Args:
        top (int): The number of top scores to retrieve.
        user (UserInDb): The authenticated user (access control only).

    Returns:
        List[HighscoreResponse]: The top N highscores.

    Raises:
        HTTPException: 404 if no highscores are found.
        HTTPException: 500 if a database error occurs.
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

def get_session_id_from_request(request: Request) -> str:
    session_id = request.cookies.get("quiz_session_id")
    if session_id is None:
        logger.warn("No session id.")
        raise HTTPException(status_code=400, detail="Session ID missing")
    return session_id


def get_score_from_redis(session_id: str) -> int:
    redis = get_redis_client()
    redis_key = f"quiz:{session_id}"
    json_data = redis.get(redis_key)
    if json_data is None:
        logger.warn("No quiz data found.")
        raise HTTPException(status_code=400, detail="No quiz data found")

    data = json.loads(json_data)
    score = data.get("score")
    if score is None:
        logger.warn("No score found in quiz data.")
        raise HTTPException(status_code=400, detail="No score found")

    return int(score)


def reset_score_in_redis(session_id: str) -> None:
    redis = get_redis_client()
    redis_key = f"quiz:{session_id}"
    redis.set(redis_key, 0)

@router.post("/api/highscore")
async def post_highscore(
    request: Request,
    user: UserInDb = Depends(get_current_user_from_cookie),
):
    """Submits the user's current score as a highscore.

    Reads score data from Redis using the quiz session ID stored in cookies.
    Validates and stores the highscore in the database. Resets the score in Redis afterward.

    Args:
        request (Request): The HTTP request containing cookies.
        user (UserInDb): The authenticated user submitting the score.

    Returns:
        dict: The newly created highscore record.

    Raises:
        HTTPException: 400 if session ID, quiz data, or score is missing.
        HTTPException: 404 if the highscore could not be created.
        HTTPException: 500 on internal server or database error.
    """
    session_id = get_session_id_from_request(request)
    score = get_score_from_redis(session_id)

    db_conn = None
    try:
        db_conn = get_connection()
        logger.info(f"Storing highscore for {user.username}: {score}")
        highscore_data = add_highscore(db_conn, user.username, score)

        reset_score_in_redis(session_id)
        return highscore_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve)) from ve
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        if db_conn:
            db_conn.close()
