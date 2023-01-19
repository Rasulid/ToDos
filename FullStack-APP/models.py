from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from DataBase import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)

    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    todos = relationship("Todos", back_populates="owner")
    address = relationship("Address", back_populates="user_address")


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates="todos")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String)
    apt_num = Column(Integer)

    user_address = relationship("User", back_populates="address")






