from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from configs.database import Base

class Rank(Base):
    __tablename__ = 'user_rank'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    min_value_to_get = Column(Integer, nullable=False)