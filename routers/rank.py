from typing import Annotated

from sqlalchemy.orm import Session

from database import SessionLocal
from models import Rank
from fastapi import APIRouter, Depends

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_depend = Annotated[Session, Depends(get_db)]

