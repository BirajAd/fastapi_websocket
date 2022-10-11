from passlib.context import CryptContext
from requests import Session

from app.schemas import UserOutput
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    user = db.query(models.User).get(email==email)
    
    if not user:
        return False, "User not found"
    return True, user

def authenticate_user(db: Session, email: str, password: str):
    status, user = get_user(db, email)
    if not status:
        return False, user
    if not verify_password(password, user.password):
        return False, "Password didn't match"
    
    return True, user

