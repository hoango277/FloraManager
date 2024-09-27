from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from configs.database import Base
from models import user, flower

class Bill(Base):
    __tablename__ = 'bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    flower_id = Column(Integer, ForeignKey('flower.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)