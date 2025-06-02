from testcontainers.mysql import MySqlContainer
import os
import time
import pytest
import mysql.connector
from app.services.database_service import connect_to_db


@pytest.mark.asyncio
async def test_connection():
    with MySqlContainer(
        "mysql:9.2.0",
        username="testuser",
        password="testpass",
        dbname="testdb"
    ) as mysql:

        # Use your retrying connection logic
        conn = connect_to_db(
            host="127.0.0.1",
            user="testuser",
            password="testpass",
            database="testdb",
            port=mysql.get_exposed_port(3306)
        )

        # Use the connection in your test
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        conn.close()
