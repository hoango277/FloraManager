from typing import Annotated

from pydantic import BaseModel, Field

from models import Flower
from .auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from .user import normalize

router = APIRouter(
    prefix="/flower",
    tags=["flower"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FlowerRequest(BaseModel):
    name: str
    price : int = Field(gt = 0)

db_depend = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/get_flower_by_{name}")
async def get_flower_by_name(name: str, db:db_depend):
    flower_return = db.query(Flower).filter(Flower.name == normalize(name)).first()
    if not flower_return:
        raise HTTPException(status_code=404, detail="Flower not found")
    return {"name": flower_return.name,
             "price": flower_return.price }

@router.post("/create_flower")
async def create_flower(flower: FlowerRequest, db:db_depend, user:user_dependency):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=403, detail="You are not able to add flower")
    flower_add = Flower(
        name=normalize(flower.name),
        price=flower.price,
    )
    db.add(flower_add)
    db.commit()

@router.delete("/delete_flower_by_{name}", status_code=204,description="Flower deleted")
async def delete_flower(name: str, db:db_depend, user:user_dependency):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=403, detail="You are not able to delete flower")
    flower_delete = db.query(Flower).filter(Flower.name == normalize(name)).first()
    if not flower_delete:
        raise HTTPException(status_code=404, detail="Flower not found")
    db.delete(flower_delete)
    db.commit()

@router.put("/update_flower_by_{name}", status_code=204,description="Flower updated")
async def update_flower(name: str, price: int, db:db_depend, user:user_dependency):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=403, detail="You are not able to update flower")
    flower_update = db.query(Flower).filter(Flower.name == normalize(name)).first()
    if not flower_update:
        raise HTTPException(status_code=404, detail="Flower not found")
    flower_update.price = price
    db.commit()



