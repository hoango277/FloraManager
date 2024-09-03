from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Rank, User
from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user

router = APIRouter(
    prefix="/rank",
    tags=["rank"],
)

def normalize(name : str):
    name = name.strip().split()
    return " ".join(i.capitalize() for i in name)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RankingReqest(BaseModel):
    name: str
    min_value_to_get: int = Field(ge = 0)


db_depend = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/create_rank")
def create_rank(request: RankingReqest, db : db_depend, user:user_dependency):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only admin can create rank")
    check = db.query(Rank).filter(
        or_(
            Rank.name == normalize(request.name),
            Rank.min_value_to_get == request.min_value_to_get
        )
    ).first()
    if check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rank already exists, please update rank!")
    db.add(Rank(
        name=normalize(request.name),
        min_value_to_get=request.min_value_to_get
    ))
    db.commit()

def set_user_rank(username:str, db : db_depend):
    current_user = db.query(User).filter(User.username == username).first()
    ranks = db.query(Rank).order_by(desc(Rank.min_value_to_get)).all()
    for rank in ranks:
        if current_user.spend >= rank.min_value_to_get:
            current_user.ranking = rank.id
            break
    db.commit()

@router.get("/get_user_rank", status_code=status.HTTP_200_OK)
def get_user_rank(db : db_depend, user:user_dependency):
    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    set_user_rank(current_user.username, db)
    rank = db.query(Rank).filter(Rank.id == current_user.ranking).first()
    return {"username": current_user.username,
        "total spend": current_user.spend,
        "User rank is" : rank.name}

@router.put("/update_rank", status_code=status.HTTP_204_NO_CONTENT)
def update_rank(db : db_depend, user:user_dependency, request:RankingReqest):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Only admin can update rank")
    rank_to_update = db.query(Rank).filter(
        or_(
            Rank.name == normalize(request.name),
            Rank.min_value_to_get == request.min_value_to_get
        )
    ).first()
    if rank_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rank does not exist")
    rank_to_update.name = normalize(request.name)
    rank_to_update.min_value_to_get = request.min_value_to_get
    db.commit()

@router.delete("/delete_rank_by_{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rank(db : db_depend, user:user_dependency, id: int):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Only admin can update rank")
    rank_to_delete = db.query(Rank).filter(Rank.id == id).first()
    if rank_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rank does not exist")
    db.delete(rank_to_delete)
    db.commit()










