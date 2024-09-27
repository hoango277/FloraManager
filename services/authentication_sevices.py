from datetime import timedelta
from os import access

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from configs.authentication import verify_password, get_password_hash, create_access_token
from configs.database import password
from exception import raise_error
from models.user import User
from schemas.authentication import Token, Register
from schemas.base_reponse import BaseResponse
from schemas.user import User as UserSchema

def get_authentication_service():
    try:
        yield AuthenticationService()
    finally:
        pass


class AuthenticationService:
    def authenticate(self, username: str, password : str, db: Session) :
            user = db.query(User).filter(User.username == username).first()
            if user is None:
                return False
            if not verify_password(password, user.hashed_password):
                return False
            access_token = create_access_token(
                user.username,
                user.id,
                user.role,
                timedelta(minutes=30)
            )
            return Token(access_token = access_token, token_type = 'Bearer')


    def create_user(self, request: Register, db : Session):
        check = db.query(User).filter(User.username == request.username).first()
        if check:
            raise raise_error(100003)
        user = User(
            username = request.username,
            hashed_password = get_password_hash(request.password),
            first_name = request.first_name,
            last_name = request.last_name,
            email = request.email,
            role=request.role,
            ranking=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserSchema(
            username = user.username,
            password = request.password,
            first_name = user.first_name,
            last_name = user.last_name,
            email = user.email,
            role = user.role,
        )

