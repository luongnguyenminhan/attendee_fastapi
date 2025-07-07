from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_session
from app.modules.users.models import User, UserCreate, UserRead
from app.modules.users.schemas import UserLogin, Token
from app.utils.security import create_access_token, verify_password, get_password_hash, create_lifetime_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_user(*, session: AsyncSession = Depends(get_session), user_create: UserCreate):
    existing_user = (await session.exec(select(User).where(User.email == user_create.email))).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_create.password)
    user = User(
        email=user_create.email, 
        hashed_password=hashed_password,
        username=user_create.username,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        is_staff=user_create.is_staff,
        organization_id=user_create.organization_id
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(user_login: UserLogin, session: AsyncSession = Depends(get_session)):
    user = (await session.exec(select(User).where(User.email == user_login.email))).first()
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to generate a lifetime token for testing
@router.post("/generate-lifetime-token", response_model=Token)
async def generate_lifetime_token(email: str, session: AsyncSession = Depends(get_session)):
    user = (await session.exec(select(User).where(User.email == email))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create a token that never expires (or expires in a very long time)
    lifetime_token = create_lifetime_token(
        data={"sub": user.email},
        secret_key=settings.LIFETIME_TOKEN_SECRET
    )
    return {"access_token": lifetime_token, "token_type": "bearer"}

