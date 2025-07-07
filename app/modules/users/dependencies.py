from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository.user_repo import UserRepo


async def get_database_session() -> AsyncSession: # type: ignore
    """Get database session locally to avoid circular import"""
    from app.core.database import get_session

    async for session in get_session():
        yield session


async def get_user_repo(db: AsyncSession = Depends(get_database_session)) -> UserRepo:
    """Dependency to get UserRepo with database session"""
    return UserRepo(db)
