from fastapi import APIRouter, Depends
from configs.authentication import get_current_user
from configs.database import get_db
from services.seller_services import get_seller_service

router = APIRouter(
    prefix="/api/seller",
    tags=["seller"],
)

@router.get("/get_all_user")
def get_all_user(user = Depends(get_current_user), db = Depends(get_db), seller_service = Depends(get_seller_service)):
    return seller_service.get_all_user(user, db)

@router.get("/get_all_bill")
def get_all_bill(user = Depends(get_current_user), db = Depends(get_db), seller_service = Depends(get_seller_service)):
    return seller_service.get_all_bill(user, db)

@router.delete("/delete_bill_by_{id}")
async def delete_bill_by_id(id: int, user = Depends(get_current_user), db = Depends(get_db), seller_service = Depends(get_seller_service)):
    return seller_service.delete_bill_by_id(user, db, id)

@router.get("/get_daily_revenue")
def get_daily_revenue(
        day : int,
        month : int,
        year : int,
        user = Depends(get_current_user),
        db = Depends(get_db),
        seller_service = Depends(get_seller_service),
):
    return seller_service.get_daily_revenue(user, db, day, month, year,)

