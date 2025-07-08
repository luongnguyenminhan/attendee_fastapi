import random
import string
from typing import Any, Dict, List, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.core.base_enums import BaseEnum
from app.core.base_model import BaseEntity


class OrganizationStatus(BaseEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Organization(BaseEntity, table=True):
    __tablename__ = "organizations"

    # Core fields
    name: str = Field(max_length=255)

    # Credit system
    centicredits: int = Field(default=0)  # Credits in centicredits (1/100th of a credit)
    version: int = Field(default=1)  # For optimistic locking

    # Webhook configuration
    is_webhooks_enabled: bool = Field(default=False)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "org_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")
    credit_transactions: List["CreditTransaction"] = Relationship(back_populates="organization")

    # Additional metadata
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSONB)

    # Domain/business logic methods
    def can_create_project(self) -> bool:
        """Check if organization can create new projects"""
        return self.status == OrganizationStatus.ACTIVE and not self.is_deleted

    def has_sufficient_credits(self, amount: float) -> bool:
        """Check if organization has sufficient credits"""
        centicredits_needed = int(amount * 100)
        return self.centicredits >= centicredits_needed

    def deduct_credits(self, amount: float) -> bool:
        """Deduct credits from organization balance. Returns True if successful."""
        centicredits_to_deduct = int(amount * 100)
        if self.centicredits >= centicredits_to_deduct:
            self.centicredits -= centicredits_to_deduct
            return True
        return False

    def add_credits(self, amount: float) -> None:
        """Add credits to organization balance"""
        centicredits_to_add = int(amount * 100)
        self.centicredits += centicredits_to_add

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

    def credits(self) -> float:
        """Get credit balance in actual credits (not centicredits)"""
        return self.centicredits / 100.0

    def get_credit_usage_stats(self) -> dict:
        """Get credit usage statistics"""
        # This would need to be implemented with database queries
        return {
            "current_balance": self.credits(),
            "total_purchased": 0.0,  # TODO: Calculate from transactions
            "total_used": 0.0,  # TODO: Calculate from transactions
            "current_month_usage": 0.0,  # TODO: Calculate current month usage
        }

    def is_low_on_credits(self, threshold: float = 10.0) -> bool:
        """Check if organization is low on credits"""
        return self.credits() < threshold

    def format_credit_balance(self) -> str:
        """Get formatted credit balance for display"""
        balance = self.credits()
        if balance >= 1000:
            return f"{balance:,.1f}"
        else:
            return f"{balance:.2f}"

    def __repr__(self):
        credit_balance = self.format_credit_balance()
        return f"<Organization {self.object_id}: {self.name} ({credit_balance} credits)>"
