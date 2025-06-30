import pytest
import socket
from fastapi.testclient import TestClient
from testcontainers.mysql import MySqlContainer
from testcontainers.redis import RedisContainer
from app.services.database_service import *
from app.services.auth_service import *
import os

SQL_FILE_PATH = os.path.abspath("init.sql")

@pytest.fixture
def password_hash():
    """Lets mock a hashed password"""
    return "hashed_password_mock"

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
    """Connecting to test container"""
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

def get_random_open_port() -> int:
    """Ask OS for an unused port and return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session", autouse=True)
def redis_container():
    """Connects to redis testcontainer"""
    fixed_port = get_random_open_port()

    container = RedisContainer("redis:8.2-m01-bookworm") \
        .with_bind_ports(6379, fixed_port)

    with container as redis:
        os.environ["REDIS_HOST"] = redis.get_container_host_ip()
        os.environ["REDIS_PORT"] = str(fixed_port)

        print(f"[TEST] Redis running on {os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}")
        yield

@pytest.fixture
def client(mysql_container):
    """Lets start the test client."""
     # Set env again for safety
    os.environ["MYSQL_URL"] = "127.0.0.1"
    os.environ["MYSQL_USER"] = "testuser"
    os.environ["MYSQL_PASSWORD"] = "testpass"
    os.environ["MYSQL_DATABASE"] = "pokedb"
    os.environ["MYSQL_PORT"] = mysql_container.get_exposed_port(3306)
    os.environ["SECRET_KEY"] = "testsecret"
    os.environ["USE_TEST_POKEMON"] = "1"
    os.environ["USE_TESTING_POKEMON"] = "1"

    from app.main import app  # Import AFTER env vars are in place
    test_client = TestClient(app)
    test_client.cookies.clear()  # Clean slate for each test
    return test_client
