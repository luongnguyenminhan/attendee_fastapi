from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.projects.repository.project_repo import ProjectRepo
from app.modules.projects.schemas.project_request import (
    CreateApiKeyRequest,
    CreateProjectRequest,
    UpdateProjectRequest,
    ValidateApiKeyRequest,
)
from app.modules.projects.schemas.project_response import (
    ApiKeyAPIResponse,
    ApiKeyCreateAPIResponse,
    ApiKeyCreateResponse,
    ApiKeyListAPIResponse,
    ApiKeyResponse,
    ApiKeyValidationAPIResponse,
    ApiKeyValidationResponse,
    ProjectAPIResponse,
    ProjectListResponse,
    ProjectPaginatedAPIResponse,
    ProjectResponse,
    ProjectStatsAPIResponse,
    ProjectStatsResponse,
)
from app.modules.users.models.user_model import User
from app.utils.security import get_current_user

router = APIRouter(tags=["Projects"])


@router.post(
    "/",
    response_model=ProjectAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
@handle_exceptions
async def create_project(
    request: CreateProjectRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Create a new project"""
    repo = ProjectRepo(session)

    project = await repo.create_project(
        name=request.name,
        organization_id=request.organization_id,
        description=request.description,
        settings=request.settings,
    )

    response_data = ProjectResponse.from_entity(project)
    return ProjectAPIResponse.success(data=response_data, message="projects.messages.created_successfully")


@router.get(
    "/organization/{organization_id}",
    response_model=ProjectPaginatedAPIResponse,
    summary="Get projects by organization",
)
@handle_exceptions
async def get_projects_by_organization(
    organization_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: str = Query(None, alias="status"),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> ProjectPaginatedAPIResponse:
    """Get paginated list of projects by organization"""
    repo = ProjectRepo(session)

    skip = (page - 1) * size

    projects_page = await repo.get_projects_by_organization(
        organization_id=organization_id,
        skip=skip,
        limit=size,
        status=status_filter,
        search=search,
    )

    # Convert entities to response schemas
    response_items = [ProjectListResponse.from_entity(proj) for proj in projects_page.items]

    projects_page.items = response_items

    return ProjectPaginatedAPIResponse.success(data=projects_page, message="projects.messages.retrieved_successfully")


@router.get("/{project_id}", response_model=ProjectAPIResponse, summary="Get project by ID")
@handle_exceptions
async def get_project(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Get project by ID"""
    repo = ProjectRepo(session)

    project = await repo.get_project_by_id(project_id)
    response_data = ProjectResponse.from_entity(project)

    return ProjectAPIResponse.success(data=response_data, message="projects.messages.retrieved_successfully")


@router.get(
    "/object/{object_id}",
    response_model=ProjectAPIResponse,
    summary="Get project by object ID",
)
@handle_exceptions
async def get_project_by_object_id(
    object_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Get project by object ID"""
    repo = ProjectRepo(session)

    project = await repo.get_project_by_object_id(object_id)
    response_data = ProjectResponse.from_entity(project)

    return ProjectAPIResponse.success(data=response_data, message="projects.messages.retrieved_successfully")


@router.patch("/{project_id}", response_model=ProjectAPIResponse, summary="Update project")
@handle_exceptions
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Update project"""
    repo = ProjectRepo(session)

    project = await repo.update_project(
        project_id=project_id,
        name=request.name,
        description=request.description,
        settings=request.settings,
    )

    response_data = ProjectResponse.from_entity(project)
    return ProjectAPIResponse.success(data=response_data, message="projects.messages.updated_successfully")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project")
@handle_exceptions
async def delete_project(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete project (soft delete)"""
    repo = ProjectRepo(session)
    await repo.delete_project(project_id)


@router.post(
    "/{project_id}/archive",
    response_model=ProjectAPIResponse,
    summary="Archive project",
)
@handle_exceptions
async def archive_project(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Archive project"""
    repo = ProjectRepo(session)

    project = await repo.archive_project(project_id)
    response_data = ProjectResponse.from_entity(project)

    return ProjectAPIResponse.success(data=response_data, message="projects.messages.archived_successfully")


@router.post(
    "/{project_id}/activate",
    response_model=ProjectAPIResponse,
    summary="Activate project",
)
@handle_exceptions
async def activate_project(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAPIResponse:
    """Activate project"""
    repo = ProjectRepo(session)

    project = await repo.activate_project(project_id)
    response_data = ProjectResponse.from_entity(project)

    return ProjectAPIResponse.success(data=response_data, message="projects.messages.activated_successfully")


@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsAPIResponse,
    summary="Get project statistics",
)
@handle_exceptions
async def get_project_stats(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectStatsAPIResponse:
    """Get project statistics"""
    repo = ProjectRepo(session)

    stats = await repo.get_project_stats(project_id)
    response_data = ProjectStatsResponse(**stats)

    return ProjectStatsAPIResponse.success(data=response_data, message="projects.messages.stats_retrieved_successfully")


# API Key Management Endpoints


@router.post(
    "/{project_id}/api-keys",
    response_model=ApiKeyCreateAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
)
@handle_exceptions
async def create_api_key(
    project_id: str,
    request: CreateApiKeyRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ApiKeyCreateAPIResponse:
    """Create a new API key for project"""
    repo = ProjectRepo(session)

    api_key, plain_key = await repo.create_api_key(project_id=project_id, name=request.name, expires_at=request.expires_at)

    response_data = ApiKeyCreateResponse.from_creation(api_key, plain_key)
    return ApiKeyCreateAPIResponse.success(data=response_data, message="projects.messages.api_key_created_successfully")


@router.get(
    "/{project_id}/api-keys",
    response_model=ApiKeyListAPIResponse,
    summary="Get project API keys",
)
@handle_exceptions
async def get_project_api_keys(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ApiKeyListAPIResponse:
    """Get all API keys for a project"""
    repo = ProjectRepo(session)

    api_keys = await repo.get_project_api_keys(project_id)

    response_items = [ApiKeyResponse.from_entity(key) for key in api_keys]

    return ApiKeyListAPIResponse.success(data=response_items, message="projects.messages.api_keys_retrieved_successfully")


@router.patch(
    "/api-keys/{api_key_id}/disable",
    response_model=ApiKeyAPIResponse,
    summary="Disable API key",
)
@handle_exceptions
async def disable_api_key(
    api_key_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ApiKeyAPIResponse:
    """Disable API key"""
    repo = ProjectRepo(session)

    api_key = await repo.disable_api_key(api_key_id)
    response_data = ApiKeyResponse.from_entity(api_key)

    return ApiKeyAPIResponse.success(data=response_data, message="projects.messages.api_key_disabled_successfully")


@router.patch(
    "/api-keys/{api_key_id}/enable",
    response_model=ApiKeyAPIResponse,
    summary="Enable API key",
)
@handle_exceptions
async def enable_api_key(
    api_key_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ApiKeyAPIResponse:
    """Enable API key"""
    repo = ProjectRepo(session)

    api_key = await repo.enable_api_key(api_key_id)
    response_data = ApiKeyResponse.from_entity(api_key)

    return ApiKeyAPIResponse.success(data=response_data, message="projects.messages.api_key_enabled_successfully")


@router.post(
    "/api-keys/validate",
    response_model=ApiKeyValidationAPIResponse,
    summary="Validate API key",
)
@handle_exceptions
async def validate_api_key(request: ValidateApiKeyRequest, session: Annotated[Session, Depends(get_session)]) -> ApiKeyValidationAPIResponse:
    """Validate API key"""
    repo = ProjectRepo(session)

    api_key = await repo.validate_api_key(request.api_key)

    if api_key:
        response_data = ApiKeyValidationResponse.valid_key(api_key)
        message = "projects.messages.api_key_valid"
    else:
        response_data = ApiKeyValidationResponse.invalid_key()
        message = "projects.messages.api_key_invalid"

    return ApiKeyValidationAPIResponse.success(data=response_data, message=message)
