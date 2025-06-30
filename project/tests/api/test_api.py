"""API tests. I amo not going to comment them all since their naming is pretty good."""
import json
import re
import pytest
import bcrypt
from app.services.database_service import *
from app.services.auth_service import *
from app.services.redis_service import get_redis_client


def create_user_with_token_pair(conn, username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    add_user(conn, username, hashed_pw)
    access_token = create_access_token({"sub": username}).access_token
    refresh_token = create_refresh_token({"sub": username}).access_token
    return access_token, refresh_token


def test_register_user(client):
    response = client.post("/api/register", json={
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 201


def test_login_user(client):
    # Register user first
    register_response = client.post("/api/register", json={
        "username": "loginuser",
        "password": "mypassword"
    })
    assert register_response.status_code == 201

    # Login: expect token to be set in cookie, not JSON
    response = client.post("/api/token", data={
        "username": "loginuser",
        "password": "mypassword"
    })
    assert response.status_code == 200

    # Check for Set-Cookie header
    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None
    assert "access_token" in cookie_header  # or your cookie name

    # Optional: check cookie exists in client for subsequent requests
    cookies = client.cookies.jar
    assert any(cookie.name == "access_token" for cookie in cookies)


def test_register_duplicate_user(client):
    client.post("/api/register", json={"username": "dupe", "password": "pw"})
    response = client.post(
        "/api/register", json={"username": "dupe", "password": "pw"})
    assert response.status_code == 400
    assert "registration failed" in response.json()["detail"].lower()


def test_login_invalid_password(client):
    client.post("/api/register",
                json={"username": "badpass", "password": "correctpw"})
    response = client.post("/api/token", data={
        "username": "badpass",
        "password": "wrongpw"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/api/token", data={
        "username": "ghost",
        "password": "nopass"
    })
    assert response.status_code == 401

# Highscores


def create_user_with_token(conn, username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    add_user(conn, username, hashed_pw)
    token = create_access_token({"sub": username}).access_token
    return token


def test_start_quiz_sets_cookie(client):
    response = client.request("GET", "/api/start_quiz", follow_redirects=False)

    # Check redirect
    assert response.status_code == 302
    assert response.headers["location"] == "/quiz"

    # Check cookie is set
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "quiz_session_id=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Path=/" in set_cookie
    assert "Max-Age=1800" in set_cookie

    match = re.search(r"quiz_session_id=([^;]+)", set_cookie)
    assert match is not None
    assert len(match.group(1)) > 0


@pytest.mark.asyncio
async def test_post_and_get_highscore(client, mysql_container):
    conn = get_connection(mysql_container.get_exposed_port(3306))
    username = "hsuser"
    password = "secure123"
    token = create_user_with_token(conn, username, password)

    # Start quiz session (prevent auto-following redirect)
    start_response = client.request(
        "GET", "/api/start_quiz", follow_redirects=False)

    # Expect a 302 redirect to /quiz
    assert start_response.status_code == 302
    assert start_response.headers["location"] == "/quiz"

    # Extract the quiz_session_id cookie
    quiz_session_id = start_response.cookies.get("quiz_session_id")
    assert quiz_session_id is not None and len(quiz_session_id) > 0

    # Seed Redis with full quiz data JSON
    redis = get_redis_client()
    quiz_key = f"quiz:{quiz_session_id}"
    quiz_data = {
        "name": "woobat",
        "score": 999,
        "submitted": False
    }
    redis.set(quiz_key, json.dumps(quiz_data))

    # Post highscore using cookies
    response = client.post(
        "/api/highscore",
        cookies={
            "access_token": token,
            "quiz_session_id": quiz_session_id
        }
    )
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Content: {response.text}"

    result = response.json()
    assert result[1] == username
    assert result[2] == 999

    # GET all highscores
    response_all = client.get(
        "/api/highscores", cookies={"access_token": token})
    assert response_all.status_code == 200
    scores = response_all.json()
    assert any(s["username"] == username and s["score"] == 999 for s in scores)

    # GET top 1 highscore
    response_top = client.get(
        "/api/highscore/1", cookies={"access_token": token})
    assert response_top.status_code == 200
    top_score = response_top.json()[0]
    assert top_score["username"] == username
    assert top_score["score"] == 999


@pytest.mark.asyncio
async def test_get_highscores_unauthorized(client):
    # /api/highscores is protected
    response = client.get("/api/highscores")
    assert response.status_code == 401  # missing or invalid token

    # /api/highscore/{top} is protected
    response = client.get("/api/highscore/1")
    assert response.status_code == 401  # No token


@pytest.mark.asyncio
async def test_post_highscore_invalid_token(client):
    response = client.post(
        "/api/highscore",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


def test_get_username(client, mysql_container):
    conn = get_connection(mysql_container.get_exposed_port(3306))
    access_token, _ = create_user_with_token_pair(conn, "whoami", "secret")

    response = client.get(
        "/api/username", cookies={"access_token": access_token})
    assert response.status_code == 200
    assert response.json()["username"] == "whoami"

    conn.close()


def test_refresh_token(client, mysql_container):
    conn = get_connection(mysql_container.get_exposed_port(3306))
    access_token, refresh_token = create_user_with_token_pair(
        conn, "refresher", "letmein")

    response = client.post("/api/token/refresh",
                           cookies={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert f"Token refreshed for refresher" in response.json()["message"]
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    conn.close()


def test_refresh_token_missing(client):
    response = client.post("/api/token/refresh")
    assert response.status_code == 401
    assert "Missing refresh token" in response.json()["detail"]


def test_logout(client, mysql_container):
    conn = get_connection(mysql_container.get_exposed_port(3306))
    access_token, refresh_token = create_user_with_token_pair(
        conn, "logouter", "bye")

    # Simulate logged-in state
    response = client.post("/api/logout", cookies={
        "access_token": access_token,
        "refresh_token": refresh_token
    })

    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"

    # Technically FastAPI's TestClient doesn't auto-remove cookies like a browser would
    # So you'd want to check that the server tried to unset them
    set_cookie_headers = response.headers.get("set-cookie")
    # logout should send Set-Cookie with deletion
    assert set_cookie_headers is not None
    assert 'access_token=""' in set_cookie_headers
    assert 'refresh_token=""' in set_cookie_headers

    conn.close()
