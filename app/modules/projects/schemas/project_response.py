from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.base_model import APIResponse, PaginatedResponse, ResponseSchema
from app.modules.projects.models.project_model import ApiKeyStatus, ProjectStatus


class ProjectResponse(ResponseSchema):
    """Project response schema"""

    id: str
    name: str
    organization_id: str
    status: ProjectStatus
    object_id: str
    description: Optional[str]
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    display_name: str
    can_create_bot: bool
    can_create_api_key: bool

    @classmethod
    def from_entity(cls, project) -> "ProjectResponse":
        """Convert Project entity to response schema"""
        return cls(
            id=str(project.id),
            name=project.name,
            organization_id=project.organization_id,
            status=project.status,
            object_id=project.object_id,
            description=project.description,
            settings=project.settings,
            created_at=project.created_at,
            updated_at=project.updated_at,
            display_name=project.get_display_name(),
            can_create_bot=project.can_create_bot(),
            can_create_api_key=project.can_create_api_key(),
        )


class ProjectListResponse(ResponseSchema):
    """Project list item response schema"""

    id: str
    name: str
    organization_id: str
    status: ProjectStatus
    object_id: str
    description: Optional[str]
    created_at: datetime

    @classmethod
    def from_entity(cls, project) -> "ProjectListResponse":
        """Convert Project entity to list response schema"""
        return cls(
            id=str(project.id),
            name=project.name,
            organization_id=project.organization_id,
            status=project.status,
            object_id=project.object_id,
            description=project.description,
            created_at=project.created_at,
        )


class ApiKeyResponse(ResponseSchema):
    """API Key response schema"""

    id: str
    name: str
    project_id: str
    object_id: str
    status: ApiKeyStatus
    last_used_at: Optional[str]
    disabled_at: Optional[str]
    expires_at: Optional[str]
    usage_count: int
    created_at: datetime
    updated_at: datetime

    # Computed fields
    display_name: str
    is_active: bool
    is_expired: bool

    @classmethod
    def from_entity(cls, api_key) -> "ApiKeyResponse":
        """Convert ApiKey entity to response schema"""
        return cls(
            id=str(api_key.id),
            name=api_key.name,
            project_id=api_key.project_id,
            object_id=api_key.object_id,
            status=api_key.status,
            last_used_at=api_key.last_used_at,
            disabled_at=api_key.disabled_at,
            expires_at=api_key.expires_at,
            usage_count=api_key.usage_count,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
            display_name=api_key.get_display_name(),
            is_active=api_key.is_active(),
            is_expired=api_key.is_expired(),
        )


class ApiKeyCreateResponse(ResponseSchema):
    """API Key creation response schema"""

    api_key: ApiKeyResponse
    plain_key: str

    @classmethod
    def from_creation(cls, api_key, plain_key: str) -> "ApiKeyCreateResponse":
        """Convert from API key creation result"""
        return cls(api_key=ApiKeyResponse.from_entity(api_key), plain_key=plain_key)


class ProjectStatsResponse(ResponseSchema):
    """Project statistics response schema"""

    project_id: str
    project_name: str
    status: str
    total_api_keys: int
    active_api_keys: int
    created_at: datetime
    last_updated: datetime


class ApiKeyValidationResponse(ResponseSchema):
    """API Key validation response schema"""

    is_valid: bool
    api_key_id: Optional[str] = None
    project_id: Optional[str] = None
    usage_count: Optional[int] = None

    @classmethod
    def valid_key(cls, api_key) -> "ApiKeyValidationResponse":
        """Create response for valid key"""
        return cls(
            is_valid=True,
            api_key_id=str(api_key.id),
            project_id=api_key.project_id,
            usage_count=api_key.usage_count,
        )

    @classmethod
    def invalid_key(cls) -> "ApiKeyValidationResponse":
        """Create response for invalid key"""
        return cls(is_valid=False)


# API Response types
ProjectAPIResponse = APIResponse[ProjectResponse]
ProjectListAPIResponse = APIResponse[List[ProjectListResponse]]
ProjectPaginatedAPIResponse = APIResponse[PaginatedResponse[ProjectListResponse]]
ProjectStatsAPIResponse = APIResponse[ProjectStatsResponse]

ApiKeyAPIResponse = APIResponse[ApiKeyResponse]
ApiKeyCreateAPIResponse = APIResponse[ApiKeyCreateResponse]
ApiKeyListAPIResponse = APIResponse[List[ApiKeyResponse]]
ApiKeyValidationAPIResponse = APIResponse[ApiKeyValidationResponse]
