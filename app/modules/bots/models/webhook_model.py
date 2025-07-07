from typing import Optional, Any, Dict
from uuid import UUID
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
import random
import string
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta

from app.core.base_model import BaseEntity
from app.core.base_enums import WebhookTriggerTypes, WebhookDeliveryAttemptStatus


class WebhookSecret(BaseEntity, table=True):
    __tablename__ = "webhook_secrets"

    # Core fields
    project_id: UUID = Field(foreign_key="project.id", index=True)
    secret: str = Field(max_length=255)
    is_active: bool = Field(default=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "whs_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    project: "Project" = Relationship(back_populates="webhook_secrets")
    webhook_subscriptions: list["WebhookSubscription"] = Relationship(
        back_populates="webhook_secret"
    )

    def __init__(self, **kwargs):
        if "secret" not in kwargs:
            kwargs["secret"] = self.generate_secret()
        super().__init__(**kwargs)

    @staticmethod
    def generate_secret() -> str:
        """Generate a secure webhook secret"""
        return secrets.token_urlsafe(32)

    def generate_signature(self, payload: bytes) -> str:
        """Generate HMAC signature for payload"""
        return hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = self.generate_signature(payload)
        return hmac.compare_digest(signature, expected)

    def __repr__(self):
        return f"<WebhookSecret {self.object_id}: {'Active' if self.is_active else 'Inactive'}>"


class WebhookSubscription(BaseEntity, table=True):
    __tablename__ = "webhook_subscriptions"

    # Core fields
    project_id: UUID = Field(foreign_key="project.id", index=True)
    bot_id: Optional[UUID] = Field(foreign_key="bots.id", index=True, default=None)
    webhook_secret_id: UUID = Field(foreign_key="webhook_secrets.id", index=True)

    # Webhook configuration
    url: str = Field(max_length=2000)
    trigger_types: list[WebhookTriggerTypes] = Field(
        default_factory=list, sa_type=JSONB
    )
    is_active: bool = Field(default=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "whs_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    project: "Project" = Relationship(back_populates="webhook_subscriptions")
    bot: Optional["Bot"] = Relationship(back_populates="webhook_subscriptions")
    webhook_secret: "WebhookSecret" = Relationship(
        back_populates="webhook_subscriptions"
    )
    delivery_attempts: list["WebhookDeliveryAttempt"] = Relationship(
        back_populates="webhook_subscription"
    )

    def is_subscribed_to(self, trigger_type: WebhookTriggerTypes) -> bool:
        """Check if subscription is active for trigger type"""
        return self.is_active and trigger_type in self.trigger_types

    def get_trigger_types_display(self) -> list[str]:
        """Get human-readable trigger types"""
        display_names = {
            WebhookTriggerTypes.BOT_STATE_CHANGE: "Bot State Changes",
            WebhookTriggerTypes.TRANSCRIPT_UPDATE: "Transcript Updates",
            WebhookTriggerTypes.CHAT_MESSAGES_UPDATE: "Chat Messages",
            WebhookTriggerTypes.PARTICIPANT_EVENTS_JOIN_LEAVE: "Participant Events",
        }
        return [display_names.get(t, str(t.value)) for t in self.trigger_types]

    def get_success_rate(self) -> float:
        """Get delivery success rate percentage"""
        if not self.delivery_attempts:
            return 0.0

        successful = sum(
            1
            for attempt in self.delivery_attempts
            if attempt.status == WebhookDeliveryAttemptStatus.SUCCESS
        )
        return (successful / len(self.delivery_attempts)) * 100

    def get_last_successful_delivery(self) -> Optional["WebhookDeliveryAttempt"]:
        """Get most recent successful delivery"""
        successful_attempts = [
            attempt
            for attempt in self.delivery_attempts
            if attempt.status == WebhookDeliveryAttemptStatus.SUCCESS
        ]
        if not successful_attempts:
            return None
        return max(successful_attempts, key=lambda a: a.created_at)

    def get_failed_deliveries_count(self) -> int:
        """Get count of failed deliveries"""
        return sum(
            1
            for attempt in self.delivery_attempts
            if attempt.status == WebhookDeliveryAttemptStatus.FAILURE
        )

    def __repr__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"<WebhookSubscription {self.object_id}: {self.url} ({status})>"


class WebhookDeliveryAttempt(BaseEntity, table=True):
    __tablename__ = "webhook_delivery_attempts"

    # Core fields
    webhook_subscription_id: str = Field(
        foreign_key="webhook_subscriptions.id", index=True
    )
    bot_id: Optional[UUID] = Field(foreign_key="bots.id", index=True, default=None)

    # Delivery details
    webhook_trigger_type: WebhookTriggerTypes = Field(index=True)
    status: WebhookDeliveryAttemptStatus = Field(
        default=WebhookDeliveryAttemptStatus.PENDING, index=True
    )

    # HTTP details
    http_status_code: Optional[int] = Field(default=None)
    response_body: Optional[str] = Field(default=None, max_length=10000)
    error_message: Optional[str] = Field(default=None, max_length=1000)

    # Payload and timing
    payload: Dict[str, Any] = Field(sa_type=JSONB)
    attempted_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)

    # Retry logic
    attempt_number: int = Field(default=1)
    next_retry_at: Optional[str] = Field(default=None)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "wda_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    webhook_subscription: "WebhookSubscription" = Relationship(
        back_populates="delivery_attempts"
    )
    bot: Optional["Bot"] = Relationship(back_populates="webhook_delivery_attempts")

    def is_pending(self) -> bool:
        """Check if delivery is pending"""
        return self.status == WebhookDeliveryAttemptStatus.PENDING

    def is_successful(self) -> bool:
        """Check if delivery was successful"""
        return self.status == WebhookDeliveryAttemptStatus.SUCCESS

    def is_failed(self) -> bool:
        """Check if delivery failed"""
        return self.status == WebhookDeliveryAttemptStatus.FAILURE

    def can_retry(self, max_attempts: int = 5) -> bool:
        """Check if delivery can be retried"""
        return (
            self.is_failed()
            and self.attempt_number < max_attempts
            and self.next_retry_at is not None
        )

    def should_retry_now(self) -> bool:
        """Check if it's time to retry"""
        if not self.can_retry() or not self.next_retry_at:
            return False

        next_retry = datetime.fromisoformat(self.next_retry_at.replace("Z", "+00:00"))
        return datetime.utcnow() >= next_retry

    def mark_pending(self) -> None:
        """Mark delivery as pending"""
        self.status = WebhookDeliveryAttemptStatus.PENDING
        self.attempted_at = self.get_current_time().isoformat()

    def mark_successful(self, http_status: int, response_body: str = None) -> None:
        """Mark delivery as successful"""
        self.status = WebhookDeliveryAttemptStatus.SUCCESS
        self.http_status_code = http_status
        self.response_body = response_body
        self.completed_at = self.get_current_time().isoformat()
        self.next_retry_at = None

    def mark_failed(
        self, error_message: str, http_status: int = None, response_body: str = None
    ) -> None:
        """Mark delivery as failed and schedule retry"""
        self.status = WebhookDeliveryAttemptStatus.FAILURE
        self.error_message = error_message
        self.http_status_code = http_status
        self.response_body = response_body
        self.completed_at = self.get_current_time().isoformat()

        # Schedule next retry with exponential backoff
        self.schedule_retry()

    def schedule_retry(self) -> None:
        """Schedule next retry with exponential backoff"""
        if self.attempt_number >= 5:  # Max attempts
            self.next_retry_at = None
            return

        # Exponential backoff: 1min, 2min, 4min, 8min, 16min
        delay_minutes = 2 ** (self.attempt_number - 1)
        next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)
        self.next_retry_at = next_retry.isoformat()

    def create_retry_attempt(self) -> "WebhookDeliveryAttempt":
        """Create a new retry attempt"""
        return WebhookDeliveryAttempt(
            webhook_subscription_id=self.webhook_subscription_id,
            bot_id=self.bot_id,
            webhook_trigger_type=self.webhook_trigger_type,
            payload=self.payload,
            attempt_number=self.attempt_number + 1,
        )

    def get_duration_ms(self) -> Optional[int]:
        """Get delivery duration in milliseconds"""
        if not self.attempted_at or not self.completed_at:
            return None

        try:
            start = datetime.fromisoformat(self.attempted_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            return int((end - start).total_seconds() * 1000)
        except:
            return None

    def get_status_display(self) -> str:
        """Get human-readable status"""
        if self.is_pending():
            return "Pending"
        elif self.is_successful():
            return f"Success ({self.http_status_code})"
        elif self.is_failed():
            status_part = f" ({self.http_status_code})" if self.http_status_code else ""
            return f"Failed{status_part}"
        return "Unknown"

    def __repr__(self):
        status = self.get_status_display()
        return f"<WebhookDeliveryAttempt {self.object_id}: {status} (Attempt {self.attempt_number})>"
