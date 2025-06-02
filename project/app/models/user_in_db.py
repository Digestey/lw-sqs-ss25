import datetime

from pydantic import BaseModel


class UserInDb(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    id: int
    username: str
    password_hash: str
    created_at: datetime.datetime
