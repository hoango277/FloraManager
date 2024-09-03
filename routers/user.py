from calendar import month
from datetime import timedelta, datetime, timezone, date
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_date
from starlette import status
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from database import SessionLocal
from passlib.context import CryptContext
from models import User, Bill, Flower
from .auth import get_current_user
from .rank import set_user_rank


router = APIRouter(
    prefix = "/users",
    tags = ["Users"],
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
    role: str = Field(default="user")



class PasswordRequest(BaseModel):
    old_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)



@router.post("/create_user", status_code=HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_depend):
    create_user = User(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        first_name=normalize(user.first_name),
        last_name=normalize(user.last_name),
        email=user.email,
        ranking = user.rank,
        role = user.role,
        spend = 0
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


@router.post("/create_new_bill", status_code=status.HTTP_201_CREATED, description="Bill added successfully")
async def create_new_bill(user: user_dependency, db : db_depend, quantity:int, flower_name:str):
    if user.get('user_role') != 'user':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only for user")
    flower_to_add = db.query(Flower).filter(Flower.name == normalize(flower_name)).first()
    current_day = datetime.now(timezone.utc).date()

    if flower_to_add is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Flower not found!")
    new_bill = Bill(
        user_id= user.get('user_id'),
        flower_id = flower_to_add.id,
        quantity= quantity,
        day=current_day.day,
        month=current_day.month,
        year = current_day.year,
        total = quantity * flower_to_add.price
    )
    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    current_user.spend += new_bill.total
    db.add(new_bill)
    db.add(current_user)
    db.commit()

@router.get("/get_monthly_bill", status_code=HTTP_200_OK)
async def get_monthly_bill(user: user_dependency, db : db_depend, month:int, year:int):
    if user.get('user_role') != 'user':
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only for user")
    try:
        date(year, month, 1)
    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid date")

    bill = db.query(Bill).filter(Bill.user_id == user.get('user_id'),
                                   Bill.month ==  month,
                                    Bill.year == year).all()
    bill_list = [
        {
            "total" : bil.total,
            "quantity": bil.quantity,
            "flower name": db.query(Flower).filter(Flower.id == bil.flower_id).first().name,
            "date": date(bil.year, bil.month, bil.day)
        }
        for bil in bill
    ]
    return bill_list

@router.get("/get_quarterly_bill", status_code=HTTP_200_OK)
async def get_quarterly_bill(year:int, user: user_dependency, db : db_depend, quarter:int = Query(gt = 0, le = 4)):
    if user.get('user_role') != 'user':
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only for user")
    start_month, end_month = quarter * 3 - 2, quarter * 3
    bill = db.query(Bill).filter(
        Bill.user_id == user.get('user_id'),
        Bill.month >= start_month,
        Bill.month <= end_month,
        Bill.year == year
    ).all()

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

@router.get("/get_yearly_bill", status_code=HTTP_200_OK)
async def get_yearly_bill(user: user_dependency, db : db_depend, year:int):
    if user.get('user_role') != 'user':
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only for user")
    try:
        date(year, 1, 1)
    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid date")

    bill = db.query(Bill).filter(Bill.user_id == user.get('user_id'),
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










