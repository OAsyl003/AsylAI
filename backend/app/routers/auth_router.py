# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.db import get_db
from app import models
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=Token)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.User).filter(models.User.email == data.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")
    user = models.User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.User).filter(models.User.email == data.email))
    user = q.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password")
    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token}


