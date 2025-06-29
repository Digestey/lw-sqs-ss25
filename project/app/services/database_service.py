"""
Module database_service

Contains the database connection functions.
"""
from fastapi import HTTPException
import time
import os
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv
from app.util import logger

# --- ENVIRONMENT VARIABLES ---

load_dotenv()

# --- META ---

CONN_POOL = None
logger = logger.get_logger(name="db_conn")

def get_pool(port=3306):
    """Create and return a global MySQL connection pool.

    If the pool has not been initialized yet, it is created with the given configuration.
    The configuration values are pulled from environment variables, with defaults provided.

    Args:
        port (int, optional): The port number for the MySQL server. Defaults to 3306.

    Returns:
        MySQLConnectionPool: A pooled connection object to the MySQL database.

    Environment Variables:
        MYSQL_URL (str): The hostname or IP of the MySQL server. Defaults to "127.0.0.1".
        MYSQL_USER (str): The username to authenticate with. Defaults to "trainer".
        MYSQL_PASSWORD (str): The password for the user. Defaults to "pokeballs".
        MYSQL_DATABASE (str): The database to connect to. Defaults to "testdb".
    """
    global CONN_POOL
    if CONN_POOL is None:
        logger.info(msg="Connection pool created.")
        CONN_POOL = pooling.MySQLConnectionPool(
            pool_name="pokedb_pool",
            pool_size=10,
            host=os.getenv("MYSQL_URL", "127.0.0.1"),
            port=port,
            user=os.getenv("MYSQL_USER", "trainer"),
            password=os.getenv("MYSQL_PASSWORD", "pokeballs"),
            database=os.getenv("MYSQL_DATABASE", "testdb")
        )
    return CONN_POOL


def is_database_healthy(
    host, user, password, database, port=3306, timeout=3, retries=5, delay=2
) -> bool:
    """
    Attempts to connect to the database to verify health, with retries.

    Args:
        host (str): Database host.
        user (str): Username.
        password (str): Password.
        database (str): Database name.
        port (int, optional): Port. Defaults to 3306.
        timeout (int, optional): Timeout in seconds. Defaults to 3.
        retries (int, optional): Retry attempts. Defaults to 5.
        delay (int, optional): Delay between retries in seconds. Defaults to 2.

    Returns:
        bool: True if connection is successful within retries, else False.
    """
    for attempt in range(retries):
        try:
            logger.info(f"[Health Check] Attempt (host {host}) {attempt + 1}/{retries}...")
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=timeout,
                use_pure=True
            )
            if conn.is_connected():
                conn.close()
                logger.info("[Health Check] Success")
                return True
        except Error as e:
            logger.warning(f"[Health Check] Connection failed: {e}")
            if attempt < retries - 1:
                logger.warning(f"[Health Check] Retrying in {delay} seconds...")
                time.sleep(delay)

    logger.warning("[Health Check] Max retries reached. Database is unhealthy.")
    return False


def get_connection(port=None):
    """Returns a connection to access the database in order to perform SQL queries.
    
    args:
        port (int): port the db is at 
        (defaults to None, if port is None, 3306 will be the default used port)
    
    """
    try:       
        port = int(port) if port else int(os.getenv("MYSQL_PORT", "3306"))
        conn = get_pool(port).get_connection()
        return conn
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise e

# --- USERS ---


def add_user(cnn, username, hashed_password):
    """Adds a user to the database.

    Args:
        cnn (connector): Database connector
        username (str): Username to be added to Database.
        hashed_password (str): Password to be added, hashed for security.

    Raises:
        ValueError: Raised, when <username> already exists
    """
    if not username.strip():
        raise ValueError("Username cannot be empty or whitespace.")
    if not hashed_password:
        raise ValueError("Password cannot be empty.")
    
    cursor = cnn.cursor(dictionary=True)
    try:
        logger.info(msg="Adding user "+username)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        cnn.commit()
    except mysql.connector.IntegrityError as exc:
        logger.error("Error while inserting into table: %s", exc)
        raise ValueError("Username already exists.") from exc
    finally:
        cursor.close()


def delete_user(cnn, username: str) -> bool:
    """
    Deletes a user from the database.

    Args:
        cnn: Database connection object.
        username (str): Username to be deleted.

    Returns:
        bool: True if a user was deleted, False if no such user found.
    """
    logger.info(f"Deleting user {username!r}")

    try:
        with cnn.cursor(dictionary=True) as cursor:
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            affected_rows = cursor.rowcount
        cnn.commit()
        return affected_rows > 0
    except Exception as e:
        logger.error(f"Failed to delete user {username!r}: {e}")
        cnn.rollback()
        raise


def get_user(cnn, username):
    """Fetches a user from the database by username

    Args:
        username (str): Username to be fetched

    Returns:
        user: returns user entry from database
    """
    cursor = cnn.cursor(dictionary=True)
    logger.info(msg="Fetching user "+username)
    try:
        cursor.execute(
            "SELECT username, password_hash, id, created_at FROM users WHERE username = %s", (
                username,)
        )
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as e:
        logger.error("Error while fetching: %s", e)
        raise HTTPException(status_code=500, detail="Database error.") from e
    finally:
        cursor.close()

# --- HIGHSCORES ---


def add_highscore(cnn, username, score):
    """Posts a new highscore

    Args:
        username (str): Username
        score (int): Achieved score

    Raises:
        ValueError: User Was not found in database
        e: Database error

    Returns:
        result: The inserted highscore
    """

    cursor = cnn.cursor()
    logger.info(msg="Adding highscore "+username+" with score: "+str(score))
    try:
        # Find user_id from username
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError("User not found")

        user_id = result[0]

        # Insert highscore using user_id
        cursor.execute(
            "INSERT INTO highscores (user_id, score) VALUES (%s, %s)", (user_id, score)
        )

        highscore_id = cursor.lastrowid

        # Fetch the inserted row
        cursor.execute(
            "SELECT h.id, u.username, h.score, h.achieved_at FROM highscores h JOIN users u ON h.user_id = u.id WHERE h.id = %s",
            (highscore_id,)
        )
        result = cursor.fetchone()
        cnn.commit()
        return result
    except Exception as e:
        logger.error("Error while adding highscore: %s", e)
        cnn.rollback()
        raise e

    finally:
        cursor.close()


def get_highscores(cnn):
    """Get all stored highscores.

    Raises:
        e: in case of db error

    Returns:
        highscores: List of highscores
    """

    cursor = cnn.cursor(dictionary=True)
    logger.info(msg="Fetching all highscores...")
    try:
        cursor.execute(
            "SELECT u.username, h.score, h.achieved_at FROM highscores h JOIN users u ON h.user_id = u.id ORDER BY h.score DESC",
        )
        highscores = cursor.fetchall()
        return highscores
    except Exception as e:
        logger.error("Error while fetching: %s", e)

        cnn.rollback()
        raise e
    finally:
        cursor.close()


def get_user_highscores(cnn, username):
    """Get the highscores from a certain user.

    Args:
        username (str): The username whose highscores are to be fetched

    Returns:
        scores: A list of all highscores archieved by the user.
    """
    try:
        with cnn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT h.score, u.username, h.achieved_at FROM highscores h
                JOIN users u ON h.user_id = u.id
                WHERE u.username = %s
                ORDER BY h.score DESC
            """, (username,))
            return cursor.fetchall()
    except Exception as e:
        logger.error("Error fetching user highscores: %s", e)
        cnn.rollback()
        raise


def get_top_highscores(cnn, limit=10):
    """Returns the top highscores

    Args:
        limit (int, optional): Number of highscores to be fetched. Defaults to 10.

    Returns:
        scores: List of highscores
    """

    try:
        with cnn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT u.username, h.score, h.achieved_at FROM highscores h
                JOIN users u ON h.user_id = u.id
                ORDER BY h.score DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
    except Exception as e:
        logger.error("Error fetching top highscores: %s", e)
        cnn.rollback()
        raise