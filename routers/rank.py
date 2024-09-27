from fastapi import APIRouter, Depends


from configs.authentication import get_current_user
from configs.database import get_db
from schemas.rank import RankRequest
from services.rank_services import get_rank_service

router = APIRouter(
    prefix="/api/rank",
    tags=["rank"],
)

@router.post("/create_rank")
def create_rank(
        rank: RankRequest,
        user = Depends(get_current_user),
        db = Depends(get_db),
        rank_service = Depends(get_rank_service)
):
    return rank_service.create_rank(user, db,rank)

@router.get("/get_all_rank")
def get_all_rank(
    db = Depends(get_db) ,
    rank_service = Depends(get_rank_service)
):
    return rank_service.get_all_rank(db)

@router.put("/update_rank_by_{id}")
def update_rank_by_id(
        id : int,
    rank: RankRequest,
    user = Depends(get_current_user),
    db = Depends(get_db),
        rank_service = Depends(get_rank_service)
):
    return rank_service.update_rank_by_id(id, db, user, rank)

@router.delete("/delete_rank_by_{id}")
def delete_rank_by_id(
        id : int,
        user = Depends(get_current_user),
        db = Depends(get_db),
        rank_service = Depends(get_rank_service)
):
    return rank_service.delete_rank_by_id(id, db, user)
