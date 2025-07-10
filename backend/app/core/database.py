import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

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

# MySQL với PyMySQL - sử dụng sync engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool,
)

# Alias sync_engine for backward compatibility
sync_engine = engine


async def get_session() -> AsyncGenerator[Session, None]:
    """Async wrapper for sync session to maintain compatibility"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_sync_session() -> Session:
    """Get synchronous session for migrations and testing"""
    return Session(sync_engine)


# Alias for backward compatibility
get_db = get_session


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[Session, None]:
    """Async context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
        await asyncio.get_event_loop().run_in_executor(None, session.commit)
    except Exception:
        await asyncio.get_event_loop().run_in_executor(None, session.rollback)
        raise
    finally:
        await asyncio.get_event_loop().run_in_executor(None, session.close)


async def create_tables():
    """Create all tables"""
    await asyncio.get_event_loop().run_in_executor(None, SQLModel.metadata.create_all, engine)


def create_tables_sync():
    """Create all tables synchronously"""
    SQLModel.metadata.create_all(sync_engine)


async def drop_tables():
    """Drop all tables (be careful!)"""
    await asyncio.get_event_loop().run_in_executor(None, SQLModel.metadata.drop_all, engine)


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
