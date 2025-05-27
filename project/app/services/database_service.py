"""
Module database_service

Contains the database connection functions.
"""
import time
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from pydantic import BaseModel

# --- ENVIRONMENT VARIABLES ---

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")
MYSQL_USERNAME = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# --- META ---


class Highscore(BaseModel):
    """Object to represent highscore
    """
    username: str
    score: int


def connect_to_db():
    """This function is used to check whether the database is reachable. It will retry to reach the
       Database 5 Times in 5 Second intervals. If the database is still not reachable, it should
       quit the application.

    Raises:
        e: Database could not be reached. Is the pokedb container up? Are the credentials correct? yeah

    Returns:
        _type_: database connection
    """
    retries = 5  # Number of retry attempts
    delay = 5  # Delay between retries in seconds

    for attempt in range(retries):
        try:
            print(
                f"Attempting to connect to MySQL (Attempt {attempt + 1}/{retries})...")
            connector = mysql.connector.connect(
                host=MYSQL_URL,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
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
                raise e  # Raise the last exception after retrying


def get_connection():
    """Returns a connection to access the database in order to perform SQL queries.

    Returns:
        PooledMYSQLConnection: Connection needed in order to perform SQL queries.
    """
    return mysql.connector.connect(
        host=MYSQL_URL,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# --- USERS ---


def add_user(username, hashed_password):
    """Adds a user to the database.

    Args:
        username (str): Username to be added to Database.
        hashed_password (str): Password to be added, hashed for security.

    Raises:
        ValueError: Raised, when <username> already exists
    """
    cnn = get_connection()
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        cnn.commit()
    except mysql.connector.IntegrityError as exc:
        raise ValueError("Username already exists.") from exc
    finally:
        cursor.close()
        cnn.close()


def delete_user(username):
    """Deletes a user

    Args:
        username (str): Username to be deleted
    """
    cnn = get_connection()
    cursor = cnn.cursor(dictionary=True)
    cursor.execute("DELETE FROM users WHERE username=(%s)", (username,))
    cnn.commit()
    cursor.close()
    cnn.close()


def get_user(username):
    """Fetches a user from the database by username

    Args:
        username (str): Username to be fetched

    Returns:
        user: returns user entry from database
    """
    cnn = get_connection()
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = %s", (
                username,)
        )
        user = cursor.fetchone()
        cursor.close()
        cnn.close()
        return user
    except mysql.connector.IntegrityError:
        print("Username not found.")
    finally:
        cursor.close()
        cnn.close()

# --- HIGHSCORES ---


def add_highscore(username, score):
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
    cnn = get_connection()
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
        cnn.close()


def get_highscores():
    """Get all stored highscores.

    Raises:
        e: in case of db error

    Returns:
        highscores: List of highscores
    """
    cnn = get_connection()
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT u.username, h.score, h.achieved_at FROM highscores h JOIN users u ON h.user_id = u.id ORDER BY h.score DESC",
        )
        highscores = cursor.fetchall()
        cursor.close()
        cnn.close()
        return highscores
    except Exception as e:
        cnn.rollback()
        raise e
    finally:
        cursor.close()
        cnn.close()


def get_user_highscores(username):
    """Get the highscores from a certain user.

    Args:
        username (str): The username whose highscores are to be fetched

    Returns:
        scores: A list of all highscores archieved by the user.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.score, u.username, h.achieved_at FROM highscores h
        JOIN users u ON h.user_id = u.id
        WHERE u.username = %s
        ORDER BY h.score DESC
    """, (username,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return scores


def get_top_highscores(limit=10):
    """Returns the top highscores

    Args:
        limit (int, optional): Number of highscores to be fetched. Defaults to 10.

    Returns:
        scores: List of highscores
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, h.score, h.achieved_at FROM highscores h
        JOIN users u ON h.user_id = u.id
        ORDER BY h.score DESC
        LIMIT %s
    """, (limit,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return scores


if __name__ == "__main__":
    connection = connect_to_db()
