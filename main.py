from fastapi import FastAPI

from configs.database import Base, engine
from  routers import authentication as auth_router
from routers import user as user_router
from routers import seller as seller_router
from routers import flower as flower_router
from routers import rank as rank_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(seller_router.router)
app.include_router(flower_router.router)
app.include_router(rank_router.router)

Base.metadata.create_all(bind=engine)