from pydantic import BaseModel


class FlowerRequest(BaseModel):
    name : str
    price : int
    quantity_left : int

