import time
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import bcrypt
from pydantic import BaseModel

# --- ENVIRONMENT VARIABLES ---

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")
MYSQL_USERNAME = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# --- META ---

class Highscore(BaseModel):
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


def add_user(username, password):
    cnn = get_connection()
    cursor = cnn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        cnn.commit()
        print("User added")
    except mysql.connector.IntegrityError:
        print("Username already exists.")
    finally:
        cursor.close()
        cnn.close()


def delete_user(username):
    cnn = get_connection()
    cursor = cnn.cursor()
    cursor.execute("DELETE FROM users WHERE username=(%s)", (username,))
    cursor.close()
    cnn.close()


def get_user(username):
    cnn = get_connection()
    cursor = cnn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (username,)
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


def verify_user(username, password):
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password hash"].encode('utf-8')):
        return True
    return False

# --- HIGHSCORES ---


def add_highscore(username, score):
    cnn = get_connection()
    cursor = cnn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, score))
        cnn.commit()
        print("Highscore added")
    except mysql.connector.IntegrityError:
        print("Highscore already exists.")
    finally:
        cursor.close()
        cnn.close()


def get_highscores():
    cnn = get_connection()
    cursor = cnn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT u.username, h.score FROM highscores h JOIN users u ON h.user_id = u.id ORDER BY h.score DESC",
        )
        highscores = cursor.fetchall()
        cursor.close()
        cnn.close()
        return highscores
    except mysql.connector.IntegrityError:
        print("Username not found.")
    finally:
        cursor.close()
        cnn.close()

def get_user_highscores(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.score, h.timestamp FROM highscores h
        JOIN users u ON h.user_id = u.id
        WHERE u.username = %s
        ORDER BY h.score DESC
    """, (username,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return scores

def get_top_highscores(limit=10):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, h.score, h.timestamp FROM highscores h
        JOIN users u ON h.user_id = u.id
        ORDER BY h.score DESC
        LIMIT %s
    """, (limit,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return scores

# Use the connect_to_db function


if __name__ == "__main__":
    connection = connect_to_db()
