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
    # os.environ["MYSQL_PORT"] = port

    conn = get_connection(port)
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
