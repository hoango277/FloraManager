from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from configs.database import Base
from models import rank

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    ranking = Column(Integer, ForeignKey('user_rank.id'), nullable=False)
    role = Column(String(255))
    spend = Column(Integer, default=0)