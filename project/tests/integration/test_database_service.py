"""Integration Tests -> User

The tests contained within this file aim to test whether the db_Connector works with
an actual testing database.
"""
from unittest.mock import patch
import bcrypt
from testcontainers.mysql import MySqlContainer
import os
import time
import pytest
import mysql.connector
from app.services.database_service import *


SQL_FILE_PATH = os.path.abspath("app/db_init/init.sql")

def run_sql_file(conn, filepath):
    """Test container initalization (based on the SQL file used for the actual initialization)

    Args:
        conn (Connection): Connection to the MySQL Container
        filepath (str): Path to SQL file
    """    
    with open(filepath, "r", encoding="utf-8") as file:
        sql_statements = file.read()

    cursor = conn.cursor()
    for statement in sql_statements.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
            # Optionally consume results if needed
            if cursor.with_rows:
                cursor.fetchall()
    conn.commit()
    cursor.close()


@pytest.fixture(scope="session")
def mysql_container():
    """Initialize the MySQL Testcontainer for testing

    Yields:
        Container: Waits for all tests to finish before shutting down the test container.
    """    
    container = MySqlContainer("mysql:9.2.0", username="testuser", password="testpass", dbname="pokedb")
    container.start()

    # Get port from the container object
    exposed_port = container.get_exposed_port(3306)

    # Now connect using correct port
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=exposed_port
    )

    # Initialize the container with highscore and user tables
    
    run_sql_file(conn, SQL_FILE_PATH)

    yield container  # Yield the actual container object

    print("Tearing down container now...")
    container.stop()
    
    
@pytest.mark.asyncio
async def test_connection(mysql_container):
    """Testing whether the connection is returned correctly.
    """        
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )    # Just testing if the connection is working
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1    
    
    # Close connection again
    
    conn.close()



@pytest.mark.asyncio
async def test_add_get_delete_user(mysql_container):
    """Testing a regluar workflow consisting of adding, requesting and deleting a user.
    """    
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt())

    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )
       # Test add_user
    add_user(conn, "sample_user", hashed_pw.decode())
    # Test get_user
    user = get_user(conn, "sample_user")
    assert user is not None
    assert user["username"] == "sample_user"
    # Test delete_user
    delete_user(conn, "sample_user")
    user = get_user(conn, "sample_user")
    assert user is None

    conn.close()
    
@pytest.mark.asyncio
async def test_invalid_user(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )
    
    user = get_user(conn, "invalid_user")
    assert user is None
    
    delete_user(conn, "invalid_user")
    
    conn.close()
    
@pytest.mark.asyncio
async def test_invalid_user(mysql_container):
    conn = connect_to_db(
    host="127.0.0.1",
    user="testuser",
    password="testpass",
    database="pokedb",
    port=mysql_container.get_exposed_port(3306)
    )
    user = get_user(conn, "invalid_user")
    assert user is None
    delete_user(conn, "invalid_user")
    conn.close()

@pytest.mark.asyncio
async def test_duplicate_user(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    add_user(conn, "dupe_user", hashed_pw)
    with pytest.raises(ValueError, match="Username already exists"):
        add_user(conn, "dupe_user", hashed_pw)
    delete_user(conn, "dupe_user")       
    conn.close()

@pytest.mark.asyncio
async def test_special_characters_in_username(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )
    username = "test_user!@#"
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    add_user(conn, username, hashed_pw)
    user = get_user(conn, username)
    assert user is not None
    assert user["username"] == username
    delete_user(conn, username)
    conn.close()

@pytest.mark.asyncio
async def test_long_username(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1",
        user="testuser",
        password="testpass",
        database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )
    long_username = "user" * 20
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    try:
        with pytest.raises(mysql.connector.DataError):
            add_user(conn, long_username, hashed_pw)
            user = get_user(conn, long_username)
            assert user is not None
            assert user["username"] == long_username
    finally:
        delete_user(conn, long_username)
        conn.close()

@pytest.mark.asyncio
async def test_add_and_fetch_highscore(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1", user="testuser", password="testpass", database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )

    # Setup: create user
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    add_user(conn, "highscore_user", hashed_pw)

    # Insert highscore
    score_data = add_highscore(conn, "highscore_user", 200)

    # score_data is a tuple: (id, username, score, achieved_at)
    assert score_data[1] == "highscore_user"  # username
    assert score_data[2] == 200               # score

    delete_user(conn, "highscore_user")
    conn.close()


@pytest.mark.asyncio
async def test_add_highscore_user_not_found(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1", user="testuser", password="testpass", database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )

    with pytest.raises(ValueError, match="User not found"):
        add_highscore(conn, "ghost_user", 999)

    conn.close()


@pytest.mark.asyncio
async def test_get_user_highscores(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1", user="testuser", password="testpass", database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )

    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    add_user(conn, "score_fetcher", hashed_pw)

    add_highscore(conn, "score_fetcher", 50)
    add_highscore(conn, "score_fetcher", 150)

    scores = get_user_highscores(conn, "score_fetcher")
    assert len(scores) == 2
    assert scores[0]["score"] >= scores[1]["score"]  # Desc order

    delete_user(conn, "score_fetcher")
    conn.close()


@pytest.mark.asyncio
async def test_get_top_highscores(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1", user="testuser", password="testpass", database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )

    # Create two users
    hashed_pw = bcrypt.hashpw("secret".encode(), bcrypt.gensalt()).decode()
    add_user(conn, "topuser1", hashed_pw)
    add_user(conn, "topuser2", hashed_pw)

    # Add highscores
    add_highscore(conn, "topuser1", 999)
    add_highscore(conn, "topuser2", 888)

    top_scores = get_top_highscores(conn)
    assert any(score["username"] == "topuser1" for score in top_scores)
    assert any(score["username"] == "topuser2" for score in top_scores)

    delete_user(conn, "topuser1")
    delete_user(conn, "topuser2")
    conn.close()


@pytest.mark.asyncio
async def test_get_highscores_empty(mysql_container):
    conn = connect_to_db(
        host="127.0.0.1", user="testuser", password="testpass", database="pokedb",
        port=mysql_container.get_exposed_port(3306)
    )

    highscores = get_highscores(conn)
    assert isinstance(highscores, list)
    assert len(highscores) == 0 

    conn.close()