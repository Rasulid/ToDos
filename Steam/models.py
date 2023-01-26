from DataBase import Base
from sqlalchemy import Boolean, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True, index=True)
    h_password = Column(String)
    is_active = Column(Boolean)

    games = relationship("Games", back_populates="user")


class Games(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    description = Column(String)
    size = Column(Integer)
    saved = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users", back_populates="games")


class GameModel(BaseModel):
    title: str
    description: str
    size: int
    saved: bool

