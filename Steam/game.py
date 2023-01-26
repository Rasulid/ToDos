from fastapi import APIRouter , Depends , HTTPException , status
from sqlalchemy.orm import Session
import models
from models import GameModel
from DataBase import engine, SessionLocal
from typing import Optional

router = APIRouter(prefix="/games",
                   tags=['Games'],
                   responses={401: {'description': "Error in game request"}})


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_oll(db: Session = Depends(get_db)):
    return db.query(models.Games).all()


@router.post('/')
async def creat_game(game: GameModel, db: Session = Depends(get_db)):
    game_models = models.Games()
    game_models.title = game.title
    game_models.description = game.description
    game_models.size = game.size
    game_models.saved = game.saved

    db.add(game_models)
    db.commit()


@router.put('/{game_id}')
async def update(game_id: int, game_model: GameModel, db: Session = Depends(get_db)):
    g_model = db.query(models.Games) \
        .filter(models.Games.id == game_id) \
        .first()

    g_model.title = game_model.title
    g_model.description = game_model.description
    g_model.size = game_model.size
    g_model.saved = game_model.saved

    db.add(g_model)
    db.commit()


@router.delete('/{game_id}')
async def delete(game_id: int, db: Session = Depends(get_db)):
    game_model = db.query(models.Games) \
        .filter(models.Games.id == game_id) \
        .delete()

    db.commit()
    return game_model
