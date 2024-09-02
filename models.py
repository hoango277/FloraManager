from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from database import Base

class Rank(Base):
    __tablename__ = 'user_rank'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    ranking = Column(Integer, ForeignKey('user_rank.id'), nullable=False)

class Flower(Base):
    __tablename__ = 'flower'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)

class Bill(Base):
    __tablename__ = 'bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    flower_id = Column(Integer, ForeignKey('flower.id'), nullable=False)
    total = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)



