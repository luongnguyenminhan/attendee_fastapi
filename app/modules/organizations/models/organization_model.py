from typing import Optional, List, Any, Dict
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.base_model import BaseEntity
from app.core.base_enums import BaseEnum


class OrganizationStatus(BaseEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Organization(BaseEntity, table=True):
    __tablename__ = "organization"

    # Core fields
    name: str = Field(index=True, max_length=255)
    centicredits: int = Field(default=500, ge=0)
    is_webhooks_enabled: bool = Field(default=True)
    status: OrganizationStatus = Field(default=OrganizationStatus.ACTIVE)

    # Additional metadata
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSONB)

    # Domain/business logic methods
    def can_create_project(self) -> bool:
        """Check if organization can create new projects"""
        return self.status == OrganizationStatus.ACTIVE and not self.is_deleted

    def has_sufficient_credits(self, required_credits: int) -> bool:
        """Check if organization has enough credits"""
        return self.centicredits >= required_credits

    def deduct_credits(self, amount: int) -> bool:
        """Deduct credits from organization"""
        if not self.has_sufficient_credits(amount):
            return False
        self.centicredits -= amount
        return True

    def add_credits(self, amount: int) -> None:
        """Add credits to organization"""
        self.centicredits += amount

    def suspend(self) -> None:
        """Suspend organization"""
        self.status = OrganizationStatus.SUSPENDED

    def activate(self) -> None:
        """Activate organization"""
        self.status = OrganizationStatus.ACTIVE

    def can_use_webhooks(self) -> bool:
        """Check if webhooks are enabled and org is active"""
        return self.is_webhooks_enabled and self.status == OrganizationStatus.ACTIVE

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.status.value})"
