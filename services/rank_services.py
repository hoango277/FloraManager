from urllib import request

from sqlalchemy import or_, desc

from configs.normalize_name import normalize
from exception import raise_error
from models.rank import Rank
from models.user import User
from schemas.rank import RankRequest


def get_rank_service():
    try:
        yield RankService()
    finally:
        pass


class RankService:
    def return_rank(self, rank_id, db):
        rank_return = db.query(Rank).filter(Rank.id == rank_id).first()
        return rank_return.name

    def create_rank(self,user, db, request: RankRequest):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        check = db.query(Rank).filter(
            or_(
                Rank.name == normalize(request.name),
                Rank.min_value_to_get == request.min_value_to_get
            )
        ).first()
        if check is not None:
            return raise_error(100012)
        db.add(Rank(
            name=normalize(request.name),
            min_value_to_get=request.min_value_to_get
        ))
        db.commit()
        return{
            'message': 'success create rank',
        }

    def get_all_rank(self, db):
        rank_return = db.query(Rank).all()
        rank_to_return = [
            {
                'name' : rank.name,
                'min_value_to_get': rank.min_value_to_get
            }
            for rank in rank_return
        ]
        return rank_to_return

    def delete_rank_by_id(self, rank_id, db, user):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        rank_to_delete = db.query(Rank).filter(Rank.id == rank_id).first()
        if rank_to_delete is None:
            return raise_error(100013)
        db.delete(rank_to_delete)
        db.commit()
        return{
            'message': 'Rank deleted!',
        }

    def update_rank_by_id(self, rank_id, db, user, rank: RankRequest):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        rank_to_update = db.query(Rank).filter(Rank.id == rank_id).first()
        if rank_to_update is None:
            return raise_error(100013)

        rank_to_update.min_value_to_get = rank.min_value_to_get
        rank_to_update.name = normalize(rank.name)
        db.commit()
        return {
            'message': 'success update rank',
        }

    def set_user_rank(self, username, db ):
        current_user = db.query(User).filter(User.username == username).first()
        ranks = db.query(Rank).order_by(desc(Rank.min_value_to_get)).all()
        for rank in ranks:
            if current_user.spend >= rank.min_value_to_get:
                current_user.ranking = rank.id
                break
        db.commit()