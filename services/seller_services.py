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


def get_seller_service():
    try:
        yield SellerService()
    finally:
        pass


class SellerService:
    def get_all_user(self, user, db):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        user_return = db.query(User).all()
        rank_service = next(get_rank_service())
        user_to_return = [
            {
                'id': cr_user.id,
                'username': cr_user.username,
                'first_name': cr_user.first_name,
                'last_name': cr_user.last_name,
                'email': cr_user.email,
                'ranking': rank_service.return_rank(cr_user.ranking, db),
                'role': cr_user.role,
                'spend': cr_user.spend
            }
            for cr_user in user_return
        ]
        return user_to_return

    def get_all_bill(self, user, db):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        bill_return = db.query(Bill, User.username, Flower.name).join(User, Bill.user_id == User.id) \
            .join(Flower, Bill.flower_id == Flower.id).all()
        if bill_return is None:
            return raise_error(100011)
        total_revenue = 0
        bill_list = [
            {
                "bill_id": bil.id,
                "username": username,
                "flower_name": name,
                "quantity": bil.quantity,
                "total": bil.total,
                "date": f"{bil.day:02d}/{bil.month:02d}/{bil.year:04d}"
            }
            for bil, username, name in bill_return
        ]
        total_revenue = sum(bil["total"] for bil in bill_list)
        return {
            "total_revenue": total_revenue,
            "bill_list": bill_list
        }

    def delete_bill_by_id(self, user, db, id:int):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        bill_to_delete = db.query(Bill).filter(Bill.id == id).first()
        if bill_to_delete is None:
            return raise_error(100011)
        db.delete(bill_to_delete)
        db.commit()
        return {
            "message" : "Bill deleted!"
        }
    def get_daily_revenue(self, user, db, day : int, month : int, year : int):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        try:
            date(year, month, day)
        except ValueError:
            return raise_error(100009)
        bill = db.query(Bill).filter(
            Bill.day == day,
            Bill.month == month,
            Bill.year == year
        ).all()
        total_daily_revenue = 0
        for bil in bill:
            total_daily_revenue += bil.total
        return {f"total revenue in {date(year, month, day)} ": total_daily_revenue}


