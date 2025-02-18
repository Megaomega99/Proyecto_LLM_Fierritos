# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    hashed_password: str

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True