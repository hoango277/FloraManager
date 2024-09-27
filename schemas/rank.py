from pydantic import BaseModel


class RankRequest(BaseModel):
    name : str
    min_value_to_get: int