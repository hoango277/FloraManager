from fastapi import APIRouter,Depends

from configs.authentication import get_current_user
from configs.database import get_db
from schemas.flower import FlowerRequest
from services.flower_services import get_flower_service

router = APIRouter(
    prefix="/api/flower",
    tags=["flower"],
)

@router.get("/get_all_flower")
def get_all_flower(db = Depends(get_db), flower_service = Depends(get_flower_service)):
    return flower_service.get_all_flower(db)

@router.post("/create_flower")
def create_flower(
        flower : FlowerRequest,
        user = Depends(get_current_user),
        db = Depends(get_db),
        flower_service = Depends(get_flower_service)

):
    return flower_service.create_flower(db, user, flower)

@router.delete("/delete_flower_by_{id}")
def delete_flower(
    id : int,
    user = Depends(get_current_user),
        db = Depends(get_db),
        flower_service = Depends(get_flower_service)
):
    return flower_service.delete_flower_by_id(db, user, id)

@router.put("/update_flower_by_{id}")
def update_flower(
    id : int,
flower : FlowerRequest,
        user=Depends(get_current_user),
        db=Depends(get_db),
        flower_service=Depends(get_flower_service)

):
    return flower_service.update_flower_by_id(db, user, flower, id)