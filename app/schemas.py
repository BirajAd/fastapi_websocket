from optparse import Option
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    email: EmailStr
    password: str
    username: str
    # first_name: Optional[str]
    # last_name: Optional[str]
    # created_at: datetime

class CreateUserOutput(BaseModel):
    email: str
    username: str