from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Use create_async_engine for async operations
engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
