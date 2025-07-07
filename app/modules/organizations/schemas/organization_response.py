from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.base_model import ResponseSchema, APIResponse, PaginatedResponse
from app.modules.organizations.models.organization_model import OrganizationStatus


class OrganizationResponse(ResponseSchema):
    """Organization response schema"""

    id: str
    name: str
    centicredits: int
    is_webhooks_enabled: bool
    status: OrganizationStatus
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    display_name: str
    can_create_project: bool
    can_use_webhooks: bool

    @classmethod
    def from_entity(cls, organization) -> "OrganizationResponse":
        """Convert Organization entity to response schema"""
        return cls(
            id=str(organization.id),
            name=organization.name,
            centicredits=organization.centicredits,
            is_webhooks_enabled=organization.is_webhooks_enabled,
            status=organization.status,
            settings=organization.settings,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
            display_name=organization.get_display_name(),
            can_create_project=organization.can_create_project(),
            can_use_webhooks=organization.can_use_webhooks(),
        )


class OrganizationListResponse(ResponseSchema):
    """Organization list item response schema"""

    id: str
    name: str
    centicredits: int
    status: OrganizationStatus
    is_webhooks_enabled: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, organization) -> "OrganizationListResponse":
        """Convert Organization entity to list response schema"""
        return cls(
            id=str(organization.id),
            name=organization.name,
            centicredits=organization.centicredits,
            status=organization.status,
            is_webhooks_enabled=organization.is_webhooks_enabled,
            created_at=organization.created_at,
        )


class OrganizationStatsResponse(ResponseSchema):
    """Organization statistics response schema"""

    total_organizations: int
    active_organizations: int
    suspended_organizations: int
    inactive_organizations: int
    total_credits: int


class CreditTransactionResponse(ResponseSchema):
    """Credit transaction response schema"""

    organization_id: str
    old_credits: int
    new_credits: int
    amount_changed: int
    operation: str


# API Response types
OrganizationAPIResponse = APIResponse[OrganizationResponse]
OrganizationListAPIResponse = APIResponse[List[OrganizationListResponse]]
OrganizationPaginatedAPIResponse = APIResponse[
    PaginatedResponse[OrganizationListResponse]
]
OrganizationStatsAPIResponse = APIResponse[OrganizationStatsResponse]
CreditTransactionAPIResponse = APIResponse[CreditTransactionResponse]
