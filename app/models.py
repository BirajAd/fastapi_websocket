from xmlrpc.client import DateTime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

class Connection(Base):
    __tablename__ = "connection"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String)

class Participance(Base):
    __tablename__ = "participance"

    id = Column(Integer, primary_key=True, index=True) 
    conn_id = Column(Integer, ForeignKey("connection.id"))
    member = Column(Integer, ForeignKey("user.id"))
    participant = relationship("Connection")

class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    sent_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime)
    content = Column(String)
    connection = Column(Integer, ForeignKey("connection.id"))
