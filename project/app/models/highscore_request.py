from pydantic import BaseModel


class HighscoreRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    username: str
    score: int
    