import datetime

from pydantic import BaseModel


class HighscoreResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    username: str
    score: int
    achieved_at: datetime.datetime
