from typing import Optional, Dict, Any
from pydantic import Field, validator

from app.core.base_model import RequestSchema
from app.modules.organizations.models.organization_model import OrganizationStatus


class CreateOrganizationRequest(RequestSchema):
    """Create organization request schema"""

    name: str = Field(
        ..., min_length=2, max_length=255, description="Organization name"
    )
    initial_credits: int = Field(default=500, ge=0, description="Initial credit amount")
    enable_webhooks: bool = Field(default=True, description="Enable webhooks")
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Organization settings"
    )

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UpdateOrganizationRequest(RequestSchema):
    """Update organization request schema"""

    name: Optional[str] = Field(
        None, min_length=2, max_length=255, description="Organization name"
    )
    is_webhooks_enabled: Optional[bool] = Field(
        None, description="Enable/disable webhooks"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None, description="Organization settings"
    )

    @validator("name")
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v


class ManageCreditsRequest(RequestSchema):
    """Manage credits request schema"""

    amount: int = Field(..., gt=0, description="Credit amount to add or deduct")
    operation: str = Field(
        ..., regex="^(add|deduct)$", description="Operation: add or deduct"
    )


class BulkStatusUpdateRequest(RequestSchema):
    """Bulk status update request schema"""

    organization_ids: list[str] = Field(
        ..., min_items=1, description="List of organization IDs"
    )
    status: OrganizationStatus = Field(..., description="New status")


class GetOrganizationsRequest(RequestSchema):
    """Get organizations request schema"""

    status: Optional[OrganizationStatus] = Field(None, description="Filter by status")
    search: Optional[str] = Field(None, min_length=1, description="Search by name")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class GetLowCreditOrganizationsRequest(RequestSchema):
    """Get low credit organizations request schema"""

    threshold: int = Field(default=100, ge=0, description="Credit threshold")
