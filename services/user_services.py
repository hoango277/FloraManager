from datetime import datetime, timezone, date

from fastapi import Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from configs.authentication import verify_password, get_password_hash, get_current_user
from exception import raise_error
from models.bill import Bill
from models.flower import Flower
from models.rank import Rank
from models.user import User
from schemas.user import PasswordRequest
from calendar import month
from datetime import timedelta, datetime, timezone, date
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_date
from starlette import status
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED

from passlib.context import CryptContext


from fastapi import HTTPException, status

from services.rank_services import get_rank_service


def get_user_service():
    try:
        yield UserService()
    finally:
        pass


class UserService:
    def get_user_info(self, db: Session, user: dict = Depends(get_current_user)):
        cr_user = db.query(User).filter(User.id == user.get('user_id')).first()
        if cr_user is None:
            return raise_error(100001)
        rank_service = next(get_rank_service())
        rank = db.query(Rank).filter(Rank.id == cr_user.ranking).first()
        rank_service.set_user_rank(cr_user.username, db)
        cr_user_to_return = {
            'id': cr_user.id,
            'username': cr_user.username,
            'first_name': cr_user.first_name,
            'last_name': cr_user.last_name,
            'email': cr_user.email,
            'ranking': rank.name,
            'role': cr_user.role,
            'spend': cr_user.spend
        }
        return cr_user_to_return

    def update_password(self, db:Session, user, password : PasswordRequest):
        cr_user = db.query(User).filter(User.id == user.get('user_id')).first()
        if cr_user is None:
            return raise_error(100001)
        if not verify_password(password.old_password, cr_user.hashed_password):
            return raise_error(100002)
        cr_user.hashed_password = get_password_hash(password.new_password)
        db.add(cr_user)
        db.commit()

    def create_new_bill(self, db:Session, user, flower_id : int, quantity: int = Query(gt = 0)):
        cr_user = db.query(User).filter(User.id == user.get('user_id')).first()
        if cr_user is None:
            return raise_error(100001)
        flower_to_add = db.query(Flower).filter(Flower.id == flower_id).first()
        if flower_to_add is None:
            return raise_error(100006)
        if quantity > flower_to_add.quantity_left:
            return raise_error(100007)
        current_day = datetime.now(timezone.utc).date()
        new_bill = Bill(
            user_id = cr_user.id,
            flower_id=flower_to_add.id,
            quantity=quantity,
            day=current_day.day,
            month=current_day.month,
            year=current_day.year,
            total=quantity * flower_to_add.price
        )
        flower_to_add.quantity_left -= quantity
        cr_user.spend += new_bill.total
        rank_service = next(get_rank_service())
        rank_service.set_user_rank(cr_user.username, db)
        db.add(new_bill)
        db.commit()
        return{
            'message' : 'bill created'
        }

    def get_monthly_bill(self ,user, db, month, year):
        if user.get('user_role') != 'user':
            return raise_error(100008)
        try:

            date(int(year), int(month), 1)
        except ValueError:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid date")
        bill = db.query(Bill).filter(Bill.user_id == user.get('user_id'),
                                     Bill.month == month,
                                     Bill.year == year).all()
        bill_list = [
            {
                "total": bil.total,
                "quantity": bil.quantity,
                "flower name": db.query(Flower).filter(Flower.id == bil.flower_id).first().name,
                "date": date(bil.year, bil.month, bil.day)
            }
            for bil in bill
        ]
        return bill_list





