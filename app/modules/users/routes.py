from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.modules.users.models import User, UserRead
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

