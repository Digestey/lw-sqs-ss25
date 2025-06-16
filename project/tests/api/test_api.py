import pytest
import bcrypt
from fastapi.testclient import TestClient
from testcontainers.mysql import MySqlContainer
from app.services.database_service import *
from app.services.auth_service import *
import os

def test_register_user(client):
    response = client.post("/api/register", json={
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 201

def test_login_user(client):
    # First, register the user
    register_response = client.post("/api/register", json={
        "username": "loginuser",
        "password": "mypassword"
    })
    assert register_response.status_code == 201  # 💡 ensure registration worked

    response = client.post("/api/token", data={
        "username": "loginuser",
        "password": "mypassword"
    })
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_user(client):
    client.post("/api/register", json={"username": "dupe", "password": "pw"})
    response = client.post("/api/register", json={"username": "dupe", "password": "pw"})
    assert response.status_code == 400
    assert "registration failed" in response.json()["detail"].lower()

def test_login_invalid_password(client):
    client.post("/api/register", json={"username": "badpass", "password": "correctpw"})
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


@pytest.mark.asyncio
async def test_post_and_get_highscore(client, mysql_container):
    conn = get_connection(mysql_container.get_exposed_port(3306))
    username = "hsuser"
    password = "secure123"
    token = create_user_with_token(conn, username, password)

    # Post a highscore
    response = client.post(
        "/api/highscore",
        json={"score": 999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result[1] == username
    assert result[2] == 999

    # Get all highscores
    response_all = client.get("/api/highscores", headers={"Authorization": f"Bearer {token}"})
    assert response_all.status_code == 200
    scores = response_all.json()
    assert any(s["username"] == username and s["score"] == 999 for s in scores)

    # Get top 1 highscore
    response_top = client.get(
        "/api/highscore/1", headers={"Authorization": f"Bearer {token}"})
    assert response_top.status_code == 200
    top_score = response_top.json()[0]
    assert top_score["username"] == username
    assert top_score["score"] == 999

    conn.close()


@pytest.mark.asyncio
async def test_get_highscores_unauthorized(client):
    # /api/highscores is protected
    response = client.get("/api/highscores")
    assert response.status_code == 401 # missing or invalid token

    # /api/highscore/{top} is protected
    response = client.get("/api/highscore/1")
    assert response.status_code == 401  # No token


@pytest.mark.asyncio
async def test_post_highscore_invalid_token(client):
    response = client.post(
        "/api/highscore",
        json={"score": 42},
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
