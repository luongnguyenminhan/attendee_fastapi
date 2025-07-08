from typing import Optional
from sqlmodel import Field, Relationship
from uuid import UUID

from app.core.base_model import BaseEntity
from app.core.base_enums import BaseEnum
from ...organizations.models.organization_model import Organization


class UserRole(BaseEnum):
    """User role enumeration"""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserStatus(BaseEnum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseEntity, table=True):
    """User entity model"""

    __tablename__ = "users"

    # Basic user information
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

    # Personal information
    first_name: str = Field(default="")
    last_name: str = Field(default="")

    # User status and permissions
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    role: UserRole = Field(default=UserRole.USER)
    is_email_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

    # Organization relationship
    organization_id: Optional[UUID] = Field(
        default=None, foreign_key="organizations.id"
    )

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="users")

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted

    def can_access_organization(self, org_id: UUID) -> bool:
        """Check if user can access specific organization"""
        return self.organization_id == org_id or self.is_superuser
