"""Highscore Data Object from the database"""
import datetime

from pydantic import BaseModel


class HighscoreResponse(BaseModel):
    """Highscore Data Object from the database.
    
    username (str): extracted Username
    score (int): archived score
    achieved_at: timestamp of when the entry was last modified/created
    """
    username: str
    score: int
    achieved_at: datetime.datetime
