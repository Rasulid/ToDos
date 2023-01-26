from fastapi import FastAPI
import models
from DataBase import engine
import game
import auth


app = FastAPI()
app.include_router(game.router)
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)


