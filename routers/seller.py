from datetime import datetime, date
from typing import Annotated

from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy.sql.functions import current_time
from starlette import status

from models import Bill, Flower, User, Rank
from .auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from .rank import normalize

router = APIRouter(
    prefix="/seller",
    tags=["seller"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_depend = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def return_rank(rank_id, db:db_depend):
    rank_return = db.query(Rank).filter(Rank.id == rank_id).first()
    return rank_return.name

@router.get("/get_all_user", status_code=status.HTTP_200_OK)
async def get_all_user(db: db_depend, user: user_dependency):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only seller can get all user")
    user_return = db.query(User).all()
    user_to_return = [
        {
            'id': cr_user.id,
            'username': cr_user.username,
            'first_name': cr_user.first_name,
            'last_name': cr_user.last_name,
            'email': cr_user.email,
            'ranking': return_rank(cr_user.ranking, db),
            'role': cr_user.role,
            'spend': cr_user.spend
        }
        for cr_user in user_return
    ]
    return user_to_return

@router.post("/get_all_bill", status_code=status.HTTP_201_CREATED)
async def get_all_bill(user: user_dependency, db : db_depend):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only seller can get bill")
    bill_return = db.query(Bill, User.username, Flower.name).join(User, Bill.user_id == User.id)\
        .join(Flower, Bill.flower_id==Flower.id).all()
    if bill_return is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    total_revenue = 0
    bill_list = [
        {
            "bill_id" : bil.id,
            "username" : username,
            "flower_name": name,
            "quantity" : bil.quantity,
            "total" : bil.total,
            "date" : f"{bil.day:02d}/{bil.month:02d}/{bil.year:04d}"
        }
        for bil, username, name in bill_return
    ]
    total_revenue = sum(bil["total"] for bil in bill_list)
    return {
            "total_revenue": total_revenue,
            "bill_list": bill_list
            }

@router.put("/update_bill", status_code=status.HTTP_204_NO_CONTENT)
async def update_bill(user: user_dependency, db : db_depend, flower_name: str, username: str, quantity: int, flower_to_change: str):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can update bill")
    flower_name = db.query(Flower).filter(Flower.name == normalize(flower_name)).first()
    flower_to_change_id = db.query(Flower).filter(Flower.name == normalize(flower_to_change)).first()
    user_find = db.query(User).filter(User.username == normalize(username)).first()
    if flower_name is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")
    bill_to_update = db.query(Bill).filter((Bill.flower_id == flower_name.id) and (Bill.user_id == user_find.id)).first()
    user_find.spend -= bill_to_update.total
    if bill_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    bill_to_update.quantity=quantity
    bill_to_update.flower_id=flower_to_change_id.id
    bill_to_update.total = quantity*flower_to_change_id.price
    user_find.spend += bill_to_update.total
    db.add(bill_to_update)
    db.add(user_find)
    db.commit()

@router.delete("/delete_bill_by_{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(user: user_dependency, db : db_depend, id : int):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can delete bill")
    bill_to_delete = db.query(Bill).filter(Bill.id == id).first()
    if bill_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    db.delete(bill_to_delete)
    db.commit()

@router.get("/get_daily_revenue", status_code=status.HTTP_200_OK)
async def get_daily_revenue(user: user_dependency, db : db_depend, day : int, month : int , year : int):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can get daily revenue")
    try:
        date(year, month, day)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid date")
    bill = db.query(Bill).filter(
        Bill.day == day,
        Bill.month == month,
        Bill.year == year
    ).all()

    total_daily_revenue = 0
    for bil in bill:
        total_daily_revenue += bil.total

    return {f"total revenue in {date(year, month, day)} ": total_daily_revenue}

@router.get("/get_monthly_revenue", status_code=status.HTTP_200_OK)
async def get_monthly_revenue(user: user_dependency, db : db_depend, month : int , year : int):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can get daily revenue")
    try:
        date(year, month, 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid date")
    bill = db.query(Bill).filter(
        Bill.month == month,
        Bill.year == year
    ).all()

    total_daily_revenue = 0
    for bil in bill:
        total_daily_revenue += bil.total

    return {
            f"total revenue in {month:02d}-{year:04d}": total_daily_revenue}

@router.get("/get_yearly_revenue", status_code=status.HTTP_200_OK)
async def get_yearly_revenue(user: user_dependency, db : db_depend, year : int):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can get daily revenue")
    try:
        date(year, 1, 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid date")
    bill = db.query(Bill).filter(
        Bill.year == year
    ).all()
    total_daily_revenue = 0
    for bil in bill:
        total_daily_revenue += bil.total

    return {
            f"total revenue in {year:04d}": total_daily_revenue}

@router.get("/get_quarterly_revenue", status_code=status.HTTP_200_OK)
async def get_monthly_revenue(year:int,user: user_dependency, db : db_depend, quarter: int = Query(gt=0, le=4)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only seller can get daily revenue")
    start_month, end_month = quarter*3-2, quarter*3
    bill = db.query(Bill).filter(
        Bill.month >= start_month,
        Bill.month <= end_month,
        Bill.year == year
    ).all()

    total_daily_revenue = 0
    for bil in bill:
        total_daily_revenue += bil.total

    return {
            f"total revenue in quarter {quarter}-{year:04d}": total_daily_revenue}




