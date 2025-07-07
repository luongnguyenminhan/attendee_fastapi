from typing import Optional, List, Any, Dict
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
import random
import string

from app.core.base_model import BaseEntity
from app.core.base_enums import BaseEnum


class ProjectStatus(BaseEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Project(BaseEntity, table=True):
    __tablename__ = "project"

    # Core fields
    name: str = Field(index=True, max_length=255)
    organization_id: str = Field(foreign_key="organization.id", index=True)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "proj_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Additional metadata
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSONB)
    description: Optional[str] = Field(default=None, max_length=1000)

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


class ApiKeyStatus(BaseEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"


class ApiKey(BaseEntity, table=True):
    __tablename__ = "apikey"

    # Core fields
    name: str = Field(max_length=255)
    project_id: str = Field(foreign_key="project.id", index=True)
    key_hash: str = Field(max_length=64, unique=True, index=True)
    status: ApiKeyStatus = Field(default=ApiKeyStatus.ACTIVE)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "key_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
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
        return (
            self.status == ApiKeyStatus.ACTIVE
            and not self.is_deleted
            and (self.expires_at is None or self.expires_at > self.get_current_time())
        )

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
