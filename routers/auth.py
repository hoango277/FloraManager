from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
form_login = Annotated[OAuth2PasswordRequestForm, Depends()]
db_depend = Annotated[Session, Depends(get_db)]
secret_key = '7f8233dbcdd6b8f089dec181ba284e609c14cc890ef32f3e71dc254730931408'
algor = 'HS256'
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class Token(BaseModel):
    access_token: str
    token_type: str



def authen_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, user_role:str ,expires_delta: timedelta):
    encode = {'sub' : username, 'id' : user_id, 'role' : user_role}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expire})
    return jwt.encode(encode, secret_key, algorithm=algor)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algor])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role : str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail= 'Cannot validate user!')
        return {'username': username, 'user_id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail= 'Cannot validate user!')




@router.post("/token", status_code=HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: form_login, db: db_depend):
    user = authen_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    return {'access_token': token, 'token_type': 'Bearer'}






