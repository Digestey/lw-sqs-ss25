import pytest
import bcrypt
from fastapi.testclient import TestClient
from testcontainers.mysql import MySqlContainer
from app.services.database_service import *
from app.services.auth_service import *
import os

SQL_FILE_PATH = os.path.abspath("app/db_init/init.sql")

def run_sql_file(conn, filepath):
    """Initializes schema in test DB."""
    with open(filepath, "r", encoding="utf-8") as f:
        statements = f.read().split(";")
        cursor = conn.cursor()
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)
                if cursor.with_rows:
                    cursor.fetchall()
        conn.commit()
        cursor.close()


@pytest.fixture(scope="session")
def mysql_container():
    container = MySqlContainer("mysql:9.2.0", username="testuser", password="testpass", dbname="pokedb")
    container.start()
    port = container.get_exposed_port(3306)

    # Override environment variables for test DB
    os.environ["MYSQL_URL"] = "127.0.0.1"
    os.environ["MYSQL_USER"] = "testuser"
    os.environ["MYSQL_PASSWORD"] = "testpass"
    os.environ["MYSQL_DATABASE"] = "pokedb"

    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=int(port)
    )
    run_sql_file(conn, SQL_FILE_PATH)
    yield container
    container.stop()

@pytest.fixture
def client(mysql_container):
     # Set env again for safety
    os.environ["MYSQL_URL"] = "127.0.0.1"
    os.environ["MYSQL_USER"] = "testuser"
    os.environ["MYSQL_PASSWORD"] = "testpass"
    os.environ["MYSQL_DATABASE"] = "pokedb"
    os.environ["MYSQL_PORT"] = mysql_container.get_exposed_port(3306)
    os.environ["SECRET_KEY"] = "testsecret"

    from app.main import app  # Import AFTER env vars are in place
    return TestClient(app)

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
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=int(mysql_container.get_exposed_port(3306))
    )
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
    response_all = client.get("/api/highscores")
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
    # /api/highscores is public, should work
    response = client.get("/api/highscores")
    assert response.status_code == 200

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
