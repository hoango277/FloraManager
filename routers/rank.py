from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Rank
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

db_depend = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/create_rank")
def create_rank(request: RankingReqest, db : db_depend):
    db.add(Rank(
        name=normalize(request.name),
    ))
    db.commit()








