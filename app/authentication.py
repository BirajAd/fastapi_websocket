from passlib.context import CryptContext
from requests import Session
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from typing import Union
from jose import JWTError, jwt
from fastapi import WebSocket, Cookie, Query, status

load_dotenv()

TOKEN_EXPIRES_MINUTES = 4*60 #4 hours
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

from app.schemas import UserOutput
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    user = db.query(models.User).filter(email==email).first()
    
    if not user:
        return False, "User not found"
    return True, user

def get_current_user(db: Session, email: str):
    user = db.query(models.User).filter(email==email).first()

    if not user:
        return False, "User not found"
    return True, user

def authenticate_user(db: Session, email: str, password: str):
    status, user = get_user(db, email)
    if not status:
        return False, user
    if not verify_password(password, user.password):
        return False, "Password didn't match"
    a_token = create_access_token(data={"sub": user.email})
    user.token = a_token
    return True, user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def email_from_token(token: str):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY)
        
        if decoded_jwt:
            return True, decoded_jwt
        else:
            return False, "invalid token"
    except Exception as e:
        return False, "invalid token"

# for websocket
async def get_query(conn_id: Union[str, None] = Query(default=None)):
   return conn_id 
