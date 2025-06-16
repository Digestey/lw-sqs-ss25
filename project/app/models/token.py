from pydantic import BaseModel

class Token(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    access_token: str
    token_type: str

