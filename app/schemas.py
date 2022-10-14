from optparse import Option

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    # date_of_birth: Optional[datetime]
    # created_at: datetime

class UserOutput(BaseModel):
    id: int
    token: str
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool

class UserInfo(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    
class LoginUser(BaseModel):
    email: EmailStr
    password: str