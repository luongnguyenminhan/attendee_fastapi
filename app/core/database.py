from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app.modules.bots.models import (
    Bot,
    BotChatMessageRequest,
    BotDebugScreenshot,
    BotEvent,
    ChatMessage,
    Credentials,
    CreditTransaction,
    Participant,
    ParticipantEvent,
    Recording,
    Utterance,
    WebhookDeliveryAttempt,
    WebhookSecret,
    WebhookSubscription,
)
from app.modules.organizations.models import Organization
from app.modules.projects.models import ApiKey, Project

# Import all models to ensure they are registered with SQLModel
from app.modules.users.models import User

settings = get_settings()

# Async engine for production
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool,
)

# Sync engine for testing and migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


def get_sync_session() -> Session:
    """Get synchronous session for migrations and testing"""
    return Session(sync_engine)


# Alias for backward compatibility
get_db = get_session


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions"""
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def create_tables_sync():
    """Create all tables synchronously"""
    SQLModel.metadata.create_all(sync_engine)


async def drop_tables():
    """Drop all tables (be careful!)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


def drop_tables_sync():
    """Drop all tables synchronously (be careful!)"""
    SQLModel.metadata.drop_all(sync_engine)


# Make sure all models are imported and registered
__all__ = [
    "engine",
    "sync_engine",
    "get_session",
    "get_db",
    "get_sync_session",
    "get_session_context",
    "create_tables",
    "create_tables_sync",
    "drop_tables",
    "drop_tables_sync",
    # Models
    "User",
    "Organization",
    "Project",
    "ApiKey",
    "Bot",
    "BotEvent",
    "BotDebugScreenshot",
    "Recording",
    "Utterance",
    "Participant",
    "ParticipantEvent",
    "ChatMessage",
    "BotChatMessageRequest",
    "CreditTransaction",
    "Credentials",
    "WebhookSecret",
    "WebhookSubscription",
    "WebhookDeliveryAttempt",
]
