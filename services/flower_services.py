from configs.normalize_name import normalize
from exception import raise_error
from models.flower import Flower
from schemas.flower import FlowerRequest



def get_flower_service():
    try:
        yield FlowerService()
    finally:
        pass


class FlowerService:
    def get_all_flower(self, db):
        flower_list = db.query(Flower).all()
        flower_list_to_return = [
            {
                "id": flower.id,
                "name": flower.name,
                "price": flower.price
            }
            for flower in flower_list
        ]
        return flower_list_to_return

    def create_flower(self, db, user, flower: FlowerRequest):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        flower_add = Flower(
            name=normalize(flower.name),
            price=flower.price,
            quantity_left=flower.quantity_left
        )
        db.add(flower_add)
        db.commit()
        return {
            'message' : 'Flower created',
        }

    def delete_flower_by_id(self, db, user, id: int):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        flower_delete = db.query(Flower).filter(Flower.id == id).first()
        if not flower_delete:
            return raise_error(100006)
        flower_delete.quantity_left = -1
        db.commit()
        return{
            'message' : 'Flower deleted',
        }

    def update_flower_by_id(self, db, user, flower: FlowerRequest, id: int):
        if user.get('user_role') != 'admin':
            return raise_error(100010)
        flower_update = db.query(Flower).filter(Flower.id == id).first()
        if not flower_update:
            return raise_error(100006)
        flower_update.name = normalize(flower.name)
        flower_update.price = flower.price
        flower_update.quantity_left = flower.quantity_left
        db.commit()
        return{
            'message' : 'Flower updated',
        }