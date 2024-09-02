from fastapi import FastAPI
import models
from database import engine
from routers import user, seller, flower, auth

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(seller.router)
app.include_router(flower.router)
models.Base.metadata.create_all(bind=engine)


