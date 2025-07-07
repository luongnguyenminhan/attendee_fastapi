from sqlmodel import SQLModel, create_engine
from app.core.config import settings

# Import all models to ensure they are registered with SQLModel.metadata
from app.modules.users.models import User
from app.modules.organizations.models import Organization
from app.modules.projects.models import Project, ApiKey
from app.modules.bots.models import (
    Bot,
    BotEvent,
    BotDebugScreenshot,
    Participant,
    ParticipantEvent,
    Recording,
    Utterance,
    Credential,
    MediaBlob,
    BotMediaRequest,
    BotChatMessageRequest,
    WebhookSecret,
    WebhookSubscription,
    WebhookDeliveryAttempt,
    ChatMessage,
    CreditTransaction,
)

engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
