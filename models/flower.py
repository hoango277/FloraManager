from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from configs.database import Base

class Flower(Base):
    __tablename__ = 'flower'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    quantity_left = Column(Integer, nullable=False)