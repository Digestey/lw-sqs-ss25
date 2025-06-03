"""
Module database_service

Contains the database connection functions.
"""
import time
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# --- ENVIRONMENT VARIABLES ---

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")
MYSQL_USERNAME = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# --- META ---


def connect_to_db(host, user, password, database, port=3306):
    """_summary_

    Args:
        host (_type_): _description_
        user (_type_): _description_
        password (_type_): _description_
        database (_type_): _description_
        port (int, optional): _description_. Defaults to 3306.

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """    
    retries = 5
    delay = 5

    for attempt in range(retries):
        try:
            print(f"Attempting to connect to MySQL (Attempt {attempt + 1}/{retries})...")
            connector = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                use_pure=True
            )

            if connector.is_connected():
                print("Successfully connected to MySQL")
                return connector
        except Error as e:
            print(f"Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Unable to connect to MySQL.")
                raise e


def get_connection():
    """Returns a connection to access the database in order to perform SQL queries.

    Returns:
        PooledMYSQLConnection: Connection needed in order to perform SQL queries.
    """
    return mysql.connector.connect(
        host=os.getenv("MYSQL_URL", "127.0.0.1"),
        port=int("3306"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "testdb"),
        use_pure=True,
        unix_socket=None
    )

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
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        cnn.commit()
    except mysql.connector.IntegrityError as exc:
        raise ValueError("Username already exists.") from exc
    finally:
        cursor.close()


def delete_user(cnn, username):
    """Deletes a user

    Args:
        username (str): Username to be deleted
    """
    cursor = cnn.cursor(dictionary=True)
    cursor.execute("DELETE FROM users WHERE username=(%s)", (username,))
    cnn.commit()
    cursor.close()

def get_user(cnn, username):
    """Fetches a user from the database by username

    Args:
        username (str): Username to be fetched

    Returns:
        user: returns user entry from database
    """
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = %s", (
                username,)
        )
        user = cursor.fetchone()
        cursor.close()
        return user
    except mysql.connector.IntegrityError:
        print("Username not found.")

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
    try:
        cursor.execute(
            "SELECT u.username, h.score, h.achieved_at FROM highscores h JOIN users u ON h.user_id = u.id ORDER BY h.score DESC",
        )
        highscores = cursor.fetchall()
        return highscores
    except Exception as e:
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
    cursor = cnn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.score, u.username, h.achieved_at FROM highscores h
        JOIN users u ON h.user_id = u.id
        WHERE u.username = %s
        ORDER BY h.score DESC
    """, (username,))
    scores = cursor.fetchall()
    cursor.close()
    return scores


def get_top_highscores(cnn, limit=10):
    """Returns the top highscores

    Args:
        limit (int, optional): Number of highscores to be fetched. Defaults to 10.

    Returns:
        scores: List of highscores
    """

    cursor = cnn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, h.score, h.achieved_at FROM highscores h
        JOIN users u ON h.user_id = u.id
        ORDER BY h.score DESC
        LIMIT %s
    """, (limit,))
    scores = cursor.fetchall()
    cursor.close()
    return scores
