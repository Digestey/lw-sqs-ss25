""" User in Database (UserInDB) Object. Represents how the user is stored within the database.
"""
import datetime

from pydantic import BaseModel


class UserInDb(BaseModel):
    """User DTO

    id (int): User ID
    username (str): username
    password_hash (str): hashed password
    created_at (datetime): timestamp of when the user was created.
    """
    id: int
    username: str
    password_hash: str
    created_at: datetime.datetime
