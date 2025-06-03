from unittest.mock import patch
import bcrypt
from testcontainers.mysql import MySqlContainer
import os
import time
import pytest
import mysql.connector
from app.services.database_service import connect_to_db, add_user, get_user, delete_user

SQL_FILE_PATH = os.path.abspath("app/db_init/init.sql")

def run_sql_file(conn, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        sql_statements = f.read()

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

    run_sql_file(conn, SQL_FILE_PATH)

    yield container  # Yield the actual container object

    print("Tearing down container now...")
    container.stop()
    
    
@pytest.mark.asyncio
async def test_connection(mysql_container):
        # Use your retrying connection logic
        conn = connect_to_db(
            host="127.0.0.1",
            user="testuser",
            password="testpass",
            database="pokedb",
            port=mysql_container.get_exposed_port(3306)
        )

        # Use the connection in your test
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        conn.close()



@pytest.mark.asyncio
async def test_add_get_delete_user(mysql_container):
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