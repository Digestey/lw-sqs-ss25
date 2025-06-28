import pytest
import json
import re
from app.services.redis_service import get_redis_client

@pytest.mark.asyncio
async def test_full_expected_workflow(client, mysql_container):
    # Register test user
    register_response = client.post("/api/register", json={
        "username": "e2euser",
        "password": "strongpass123"
    })
    assert register_response.status_code == 201

    # Login
    login_response = client.post("/api/token", data={
        "username": "e2euser",
        "password": "strongpass123"
    })
    assert login_response.status_code == 200

    access_token = login_response.cookies.get("access_token")
    assert access_token is not None, "No access_token cookie set"

    # Step 1: Start quiz session — DO NOT follow redirects
    start_response = client.get("/api/start_quiz", follow_redirects=False)
    assert start_response.status_code == 302  # Redirect expected

    # Manually parse quiz_session_id from Set-Cookie header
    set_cookie = start_response.headers.get("set-cookie")
    assert set_cookie is not None and "quiz_session_id=" in set_cookie

    match = re.search(r"quiz_session_id=([^;]+)", set_cookie)
    quiz_session_id = match.group(1)
    assert quiz_session_id is not None

    # Step 2: Seed Redis with score for this session
    redis = get_redis_client()
    quiz_key = f"quiz:{quiz_session_id}"
    quiz_data = {
        "name": "somepokemon",
        "score": 1337,
        "submitted": False
    }
    redis.set(quiz_key, json.dumps(quiz_data))

    # Step 3: Post highscore using quiz_session_id cookie and access_token
    hs_response = client.post(
        "/api/highscore",
        cookies={"access_token": access_token, "quiz_session_id": quiz_session_id}
    )
    assert hs_response.status_code == 200, f"Expected status 200 but got {hs_response.status_code}. Response content: {hs_response.text}"

    result = hs_response.json()
    assert result[1] == "e2euser"
    assert result[2] == 1337

    # Request highscores, use auth token
    get_response = client.get(
        "/api/highscores",
        cookies={"access_token": access_token}
    )
    assert get_response.status_code == 200
    assert any(score["username"] == "e2euser" and score["score"] == 1337 for score in get_response.json())
