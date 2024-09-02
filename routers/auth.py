from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_depend = Annotated[Session, Depends(get_db)]