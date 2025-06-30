"""Redis Service. The connector to everything Redis-related. in this case Redis is used as a temp storage for 
questions and user scores during their partitipation in a quiz
"""
import json
import os
import time
import redis
from app.util.logger import get_logger

logger = get_logger("Redis")


def create_redis_client():
    """Returns a redis client to connect to a redis container.

    Returns:
        Redis: Redis connector
    """
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", 6379))
    logger.info(f"Connecting to Redis at {host}:{port}")
    return redis.Redis(
        host=host,
        port=port,
        db=0,
        decode_responses=True
    )


def get_redis_client():
    """ Returns a redis client. a wrapper function to build lazy initalization

    Returns:
        Redis: Redis client
    """
    return create_redis_client()


def is_redis_healthy(retries=5, delay=1):
    """Redis health Check. Tries to connect to redis service and will produce a warinig
    if that is not possible. Intended to be run before the uvicorn process is starting.

    Args:
        retries (int, optional): Number of retries. Defaults to 5.
        delay (int, optional): Delay between each retry. Defaults to 1.

    Returns:
        bool: Returns True if the Health Check was successfull. False otherwise
    """
    client = get_redis_client()
    for _ in range(retries):
        try:
            client.ping()
            return True
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Redis not reachable: {e}")
            time.sleep(delay)
    return False


def _key(client_id: str) -> str:
    """Generate the Redis key for storing quiz state for a specific client.

    Args:
        client_id (str): The unique identifier for the client.

    Returns:
        str: The Redis key used to store the quiz state.
    """
    return f"quiz:{client_id}"


def get_state(client_id: str):
    """Retrieve the current quiz state for a given client from Redis.

    Args:
        client_id (str): The unique identifier for the client.

    Returns:
        dict | None: The quiz state as a dictionary if present, otherwise None.
    """
    client = get_redis_client()
    state = client.get(_key(client_id))
    return json.loads(state) if state else None


def set_state(client_id: str, pokemon: dict):
    """Set or update the current quiz state for a given client in Redis.

    Args:
        client_id (str): The unique identifier for the client.
        pokemon (dict): The current quiz data to store.
    """
    client = get_redis_client()
    client.setex(_key(client_id), 1800, json.dumps(pokemon))


def clear_state(client_id: str):
    """Clear the quiz state for a given client from Redis.

    Args:
        client_id (str): The unique identifier for the client.
    """
    client = get_redis_client()
    client.delete(_key(client_id))


def _score_key(session_id: str) -> str:
    """Generate the Redis key for storing quiz score for a specific session.

    Args:
        session_id (str): The unique identifier for the session.

    Returns:
        str: The Redis key used to store the quiz score.
    """
    return f"quiz:{session_id}:score"


def get_score(session_id: str) -> int:
    """Retrieve the current score for a given session from Redis.

    Args:
        session_id (str): The unique identifier for the session.

    Returns:
        int: The score value, or 0 if not found.
    """
    client = get_redis_client()
    score = client.get(_score_key(session_id))
    return int(score) if score else 0


def increment_score(session_id: str, value: int = 25):
    """Increment the score for a given session in Redis.

    Args:
        session_id (str): The unique identifier for the session.
        value (int, optional): Amount to increment the score by. Defaults to 25.
    """
    client = get_redis_client()
    client.incrby(_score_key(session_id), value)
    client.expire(_score_key(session_id), 1800)


def reset_score(session_id: str):
    """Reset the quiz score for a given session in Redis.

    Args:
        session_id (str): The unique identifier for the session.
    """
    client = get_redis_client()
    client.delete(_score_key(session_id))
