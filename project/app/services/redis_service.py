import redis
import json
import os
import time
from app.util.logger import get_logger

logger = get_logger("Redis")

def create_redis_client():
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    logger.info(f"Connecting to Redis at {host}:{port}")
    return redis.Redis(
        host=host,
        port=port,
        db=0,
        decode_responses=True
    )

def get_redis_client():
    return create_redis_client()

def is_redis_healthy(retries=5, delay=1):
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
    return f"quiz:{client_id}"

def get_state(client_id: str):
    client = get_redis_client()
    state = client.get(_key(client_id))
    return json.loads(state) if state else None

def set_state(client_id: str, pokemon: dict):
    client = get_redis_client()
    client.setex(_key(client_id), 1800, json.dumps(pokemon))

def clear_state(client_id: str):
    client = get_redis_client()
    client.delete(_key(client_id))

def _score_key(session_id: str) -> str:
    return f"quiz:{session_id}:score"

def get_score(session_id: str) -> int:
    client = get_redis_client()
    score = client.get(_score_key(session_id))
    return int(score) if score else 0

def increment_score(session_id: str, value: int = 25):
    client = get_redis_client()
    client.incrby(_score_key(session_id), value)
    client.expire(_score_key(session_id), 1800)

def reset_score(session_id: str):
    client = get_redis_client()
    client.delete(_score_key(session_id))