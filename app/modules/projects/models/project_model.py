import random
import string
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.dialects.mysql import JSON
from sqlmodel import Field, Relationship

from app.core.base_enums import BaseEnum
from app.core.base_model import BaseEntity


class ProjectStatus(BaseEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Project(BaseEntity, table=True):
    __tablename__ = "project"

    # Core fields
    name: str = Field(index=True, max_length=255)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "proj_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Additional metadata
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSON)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Relationships
    organization: "Organization" = Relationship(back_populates="projects")
    bots: List["Bot"] = Relationship(back_populates="project")
    credentials: List["Credentials"] = Relationship(back_populates="project")
    webhook_secrets: List["WebhookSecret"] = Relationship(back_populates="project")
    webhook_subscriptions: List["WebhookSubscription"] = Relationship(back_populates="project")

    # Domain/business logic methods
    def can_create_bot(self) -> bool:
        """Check if project can create new bots"""
        return self.status == ProjectStatus.ACTIVE and not self.is_deleted

    def can_create_api_key(self) -> bool:
        """Check if project can create new API keys"""
        return self.status == ProjectStatus.ACTIVE and not self.is_deleted

    def archive(self) -> None:
        """Archive project"""
        self.status = ProjectStatus.ARCHIVED

    def activate(self) -> None:
        """Activate project"""
        self.status = ProjectStatus.ACTIVE

    def deactivate(self) -> None:
        """Deactivate project"""
        self.status = ProjectStatus.INACTIVE

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.status.value})"

    def get_active_bots_count(self) -> int:
        """Get count of active bots"""
        return len([bot for bot in self.bots if bot.is_active()])

    def get_total_bots_count(self) -> int:
        """Get total count of bots"""
        return len(self.bots)

    def get_credentials_by_type(self, credential_type) -> Optional["Credentials"]:
        """Get active credentials of specific type"""
        for cred in self.credentials:
            if cred.credential_type == credential_type and cred.is_active:
                return cred
        return None

    def has_credentials_for_type(self, credential_type) -> bool:
        """Check if project has active credentials for type"""
        return self.get_credentials_by_type(credential_type) is not None

    def get_active_webhook_subscriptions(self) -> List["WebhookSubscription"]:
        """Get all active webhook subscriptions"""
        return [sub for sub in self.webhook_subscriptions if sub.is_active]

    def has_webhook_subscriptions(self) -> bool:
        """Check if project has any active webhook subscriptions"""
        return len(self.get_active_webhook_subscriptions()) > 0

    def get_webhook_secret(self) -> Optional["WebhookSecret"]:
        """Get active webhook secret"""
        for secret in self.webhook_secrets:
            if secret.is_active:
                return secret
        return None

    def create_webhook_secret(self) -> "WebhookSecret":
        """Create a new webhook secret"""
        # Mark existing secrets as inactive
        for secret in self.webhook_secrets:
            secret.is_active = False

        # Create new secret
        from app.modules.bots.models.webhook_model import WebhookSecret

        new_secret = WebhookSecret(project_id=self.id)
        return new_secret

    def can_create_bot(self) -> tuple[bool, Optional[str]]:
        """Check if project can create a new bot"""
        if not self.is_active:
            return False, "Project is not active"

        if not self.organization.is_active():
            return False, "Organization is not active"

        # Check if organization has sufficient credits
        if self.organization.is_low_on_credits():
            return False, "Organization has insufficient credits"

        return True, None

    def get_project_stats(self) -> dict:
        """Get project statistics"""
        return {
            "total_bots": self.get_total_bots_count(),
            "active_bots": self.get_active_bots_count(),
            "total_credentials": len(self.credentials),
            "active_credentials": len([c for c in self.credentials if c.is_active]),
            "webhook_subscriptions": len(self.get_active_webhook_subscriptions()),
            "has_webhook_secret": self.get_webhook_secret() is not None,
        }

    def activate(self) -> None:
        """Activate the project"""
        self.status = ProjectStatus.ACTIVE

    def deactivate(self) -> None:
        """Deactivate the project"""
        self.status = ProjectStatus.INACTIVE

    def get_display_name(self) -> str:
        """Get formatted display name"""
        status = "Active" if self.status == ProjectStatus.ACTIVE else "Inactive"
        return f"{self.name} ({status})"

    def __repr__(self):
        bot_count = self.get_total_bots_count()
        status = "Active" if self.status == ProjectStatus.ACTIVE else "Inactive"
        return f"<Project {self.object_id}: {self.name} ({bot_count} bots, {status})>"


class ApiKeyStatus(BaseEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"


class ApiKey(BaseEntity, table=True):
    __tablename__ = "apikey"

    # Core fields
    name: str = Field(max_length=255)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    key_hash: str = Field(max_length=64, unique=True, index=True)
    status: ApiKeyStatus = Field(default=ApiKeyStatus.ACTIVE)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "key_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Additional fields
    last_used_at: Optional[str] = Field(default=None)
    disabled_at: Optional[str] = Field(default=None)
    expires_at: Optional[str] = Field(default=None)

    # Usage tracking
    usage_count: int = Field(default=0, ge=0)

    # Domain/business logic methods
    def is_active(self) -> bool:
        """Check if API key is active"""
        return self.status == ApiKeyStatus.ACTIVE and not self.is_deleted and (self.expires_at is None or self.expires_at > self.get_current_time())

    def disable(self) -> None:
        """Disable API key"""
        self.status = ApiKeyStatus.DISABLED
        self.disabled_at = self.get_current_time()

    def enable(self) -> None:
        """Enable API key"""
        self.status = ApiKeyStatus.ACTIVE
        self.disabled_at = None

    def record_usage(self) -> None:
        """Record API key usage"""
        self.usage_count += 1
        self.last_used_at = self.get_current_time()

    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if self.expires_at is None:
            return False
        return self.expires_at <= self.get_current_time()

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.status.value})"
