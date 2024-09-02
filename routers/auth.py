from email.policy import default
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK

from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from models import User
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
form_login = Annotated[OAuth2PasswordRequestForm, Depends()]
db_depend = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=50)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=50)
    rank: int = Field(default=1)

@router.post("/auth/create_user", status_code=HTTP_201_CREATED)
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


def authen_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return True

@router.post("/auth/login", status_code=HTTP_200_OK)
async def login(form_data: form_login, db: db_depend):
    if not authen_user(db, form_data.username, form_data.password):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Incorrect username or password")
    return {"message": "You are now logged in!"}

@router.get("/get_all_users")
async def get_all_users(db: db_depend):
    users = db.query(User).all()
    return users






