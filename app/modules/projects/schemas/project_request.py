from typing import Optional, Dict, Any
from pydantic import Field, validator

from app.core.base_model import RequestSchema
from app.modules.projects.models.project_model import ProjectStatus


class CreateProjectRequest(RequestSchema):
    """Create project request schema"""

    name: str = Field(..., min_length=2, max_length=255, description="Project name")
    organization_id: str = Field(..., description="Organization ID")
    description: Optional[str] = Field(
        None, max_length=1000, description="Project description"
    )
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Project settings"
    )

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UpdateProjectRequest(RequestSchema):
    """Update project request schema"""

    name: Optional[str] = Field(
        None, min_length=2, max_length=255, description="Project name"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Project description"
    )
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")

    @validator("name")
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v


class GetProjectsRequest(RequestSchema):
    """Get projects request schema"""

    organization_id: str = Field(..., description="Organization ID")
    status: Optional[ProjectStatus] = Field(None, description="Filter by status")
    search: Optional[str] = Field(None, min_length=1, description="Search by name")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class CreateApiKeyRequest(RequestSchema):
    """Create API key request schema"""

    name: str = Field(..., min_length=2, max_length=255, description="API key name")
    expires_at: Optional[str] = Field(None, description="Expiry date (ISO format)")

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class GetApiKeysRequest(RequestSchema):
    """Get API keys request schema"""

    project_id: str = Field(..., description="Project ID")
    status: Optional[str] = Field(None, description="Filter by status")
    search: Optional[str] = Field(None, min_length=1, description="Search by name")


class ValidateApiKeyRequest(RequestSchema):
    """Validate API key request schema"""

    api_key: str = Field(..., min_length=10, description="API key to validate")
