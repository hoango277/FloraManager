import traceback
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from configs.authentication import get_current_user
from configs.database import get_db
from exception import raise_error
from schemas.user import PasswordRequest
from services.user_services import get_user_service

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

@router.post("/get_user_info")
def get_user_info(db = Depends(get_db), user = Depends(get_current_user), user_service = Depends(get_user_service)):
    user = user_service.get_user_info(db, user)
    if not user:
        return raise_error(100001)
    return user

@router.put("/update_user_password")
def update_user_password(
    password : PasswordRequest,
    db = Depends(get_db),
    user = Depends(get_current_user),
    user_service = Depends(get_user_service),
):
        try:
            user_service.update_password(db, user, password)
            return {
                'message': 'Password updated successfully'
            }
        except Exception :
            return raise_error(100005)

@router.post("/create_new_bill")
def create_new_bill(
        flower_id:int,
        quantity : int ,
        db = Depends(get_db),
        user = Depends(get_current_user),
        user_service = Depends(get_user_service)
):
    if quantity <= 0:
        return raise_error(100014)
    return user_service.create_new_bill(db ,user, flower_id, quantity)


@router.get("/get_monthly_bills")
def get_monthly_bills(year, month, db = Depends(get_db), user = Depends(get_current_user), user_service = Depends(get_user_service)
                      ):
    return user_service.get_monthly_bill(user, db, month, year)





