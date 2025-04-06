import time
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

def connect_to_db():
    retries = 5  # Number of retry attempts
    delay = 5  # Delay between retries in seconds

    for attempt in range(retries):
        try:
            print(f"Attempting to connect to MySQL (Attempt {attempt + 1}/{retries})...")
            connector = mysql.connector.connect(
                host=MYSQL_URL,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD
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

# Use the connect_to_db function
connection = connect_to_db()

# Continue with your application logic here