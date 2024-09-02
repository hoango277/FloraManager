from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from database import SessionLocal
from passlib.context import CryptContext
from models import User
from .auth import get_current_user


router = APIRouter(
    prefix = "/users",
    tags = ["Users"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_depend = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_dependency = Annotated[dict, Depends(get_current_user)]



class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=50)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=50)
    rank: int = Field(default=1)



class PasswordRequest(BaseModel):
    old_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)



@router.post("/create_user", status_code=HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_depend):
    create_user = User(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        ranking = user.rank
    )
    db.add(create_user)
    db.commit()

@router.put("/update_password", status_code=HTTP_200_OK)
async def update_password(current_user: user_dependency, db: db_depend, password: PasswordRequest):
    user = db.query(User).filter(User.id == current_user.get('user_id')).first()
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found!")
    if not bcrypt_context.verify(password.old_password, user.hashed_password):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="Incorrect password.")

    user.hashed_password = bcrypt_context.hash(password.new_password)
    db.commit()
    raise HTTPException(status_code=HTTP_200_OK, detail="Password updated successfully!")









