# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.api.auth import get_current_user, get_current_user_id
from typing import List

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user(
    user_update: UserSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}