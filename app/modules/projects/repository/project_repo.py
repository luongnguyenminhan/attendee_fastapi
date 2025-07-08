import hashlib
import secrets
from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session

from app.core.base_model import PaginatedResponse
from app.exceptions.exception import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.modules.projects.dal.project_dal import ApiKeyDAL, ProjectDAL
from app.modules.projects.models.project_model import (
    ApiKey,
    ApiKeyStatus,
    Project,
    ProjectStatus,
)


class ProjectRepo:
    """Project Repository - Business Logic Layer"""

    def __init__(self, session: Session):
        self.session = session
        self.project_dal = ProjectDAL()
        self.api_key_dal = ApiKeyDAL()
        self.project_dal.set_session(session)
        self.api_key_dal.set_session(session)

    async def create_project(
        self,
        name: str,
        organization_id: str,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create new project with validation"""
        # Validate input
        if not name or len(name.strip()) < 2:
            raise ValidationException("projects.validation.name_too_short")

        if not organization_id:
            raise ValidationException("projects.validation.organization_required")

        # Check name uniqueness within organization
        existing = await self.project_dal.get_by_organization_and_name(organization_id, name.strip())
        if existing:
            raise ConflictException("projects.errors.name_already_exists")

        # Create project
        project = Project(
            name=name.strip(),
            organization_id=organization_id,
            description=description,
            status=ProjectStatus.ACTIVE,
            settings=settings or {},
        )

        return await self.project_dal.create(project)

    async def get_project_by_id(self, project_id: str) -> Project:
        """Get project by ID with validation"""
        project = await self.project_dal.get_by_id(project_id)
        if not project:
            raise NotFoundException("projects.errors.not_found")
        return project

    async def get_project_by_object_id(self, object_id: str) -> Project:
        """Get project by object_id"""
        project = await self.project_dal.get_by_object_id(object_id)
        if not project:
            raise NotFoundException("projects.errors.not_found")
        return project

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Update project with validation"""
        project = await self.get_project_by_id(project_id)

        # Validate new name if provided
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ValidationException("projects.validation.name_too_short")

            # Check name uniqueness within organization
            if name.strip() != project.name:
                existing = await self.project_dal.get_by_organization_and_name(project.organization_id, name.strip())
                if existing:
                    raise ConflictException("projects.errors.name_already_exists")

            project.name = name.strip()

        if description is not None:
            project.description = description

        if settings is not None:
            project.settings = settings

        return await self.project_dal.update(project)

    async def delete_project(self, project_id: str) -> bool:
        """Soft delete project and disable all API keys"""
        project = await self.get_project_by_id(project_id)

        # Disable all API keys first
        await self.api_key_dal.bulk_disable_by_project(project_id)

        # Soft delete project
        return await self.project_dal.delete(project)

    async def get_projects_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[Project]:
        """Get paginated projects by organization with filters"""

        if status and search:
            # Complex filtering
            projects = await self.project_dal.get_by_status(status, organization_id)
            if search:
                projects = [proj for proj in projects if search.lower() in proj.name.lower()]
            total = len(projects)
            start = skip
            end = start + limit
            items = projects[start:end]
        elif status:
            projects = await self.project_dal.get_by_status(status, organization_id)
            total = len(projects)
            start = skip
            end = start + limit
            items = projects[start:end]
        elif search:
            items = await self.project_dal.search_by_name(search, organization_id)
            total = len(items)
            start = skip
            end = start + limit
            items = items[start:end]
        else:
            # Get all by organization then paginate
            all_projects = await self.project_dal.get_by_organization_id(organization_id)
            total = len(all_projects)
            start = skip
            end = start + limit
            items = all_projects[start:end]

        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit

        return PaginatedResponse[Project](
            items=items,
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def archive_project(self, project_id: str) -> Project:
        """Archive project"""
        project = await self.get_project_by_id(project_id)
        project.archive()
        return await self.project_dal.update(project)

    async def activate_project(self, project_id: str) -> Project:
        """Activate project"""
        project = await self.get_project_by_id(project_id)
        project.activate()
        return await self.project_dal.update(project)

    # API Key management methods
    async def create_api_key(self, project_id: str, name: str, expires_at: Optional[str] = None) -> Tuple[ApiKey, str]:
        """Create new API key and return key + plain text"""
        project = await self.get_project_by_id(project_id)

        if not project.can_create_api_key():
            raise ValidationException("projects.validation.cannot_create_api_key")

        # Validate input
        if not name or len(name.strip()) < 2:
            raise ValidationException("projects.validation.api_key_name_too_short")

        # Generate API key
        plain_key = f"ak_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

        # Create API key
        api_key = ApiKey(
            name=name.strip(),
            project_id=project_id,
            key_hash=key_hash,
            expires_at=expires_at,
            status=ApiKeyStatus.ACTIVE,
        )

        created_key = await self.api_key_dal.create(api_key)
        return created_key, plain_key

    async def get_api_key_by_id(self, api_key_id: str) -> ApiKey:
        """Get API key by ID"""
        api_key = await self.api_key_dal.get_by_id(api_key_id)
        if not api_key:
            raise NotFoundException("projects.errors.api_key_not_found")
        return api_key

    async def get_api_key_by_hash(self, key_hash: str) -> ApiKey:
        """Get API key by hash for authentication"""
        api_key = await self.api_key_dal.get_by_key_hash(key_hash)
        if not api_key:
            raise NotFoundException("projects.errors.api_key_not_found")
        return api_key

    async def get_project_api_keys(self, project_id: str) -> List[ApiKey]:
        """Get all API keys for a project"""
        await self.get_project_by_id(project_id)  # Validate project exists
        return await self.api_key_dal.get_by_project_id(project_id)

    async def disable_api_key(self, api_key_id: str) -> ApiKey:
        """Disable API key"""
        api_key = await self.get_api_key_by_id(api_key_id)
        api_key.disable()
        return await self.api_key_dal.update(api_key)

    async def enable_api_key(self, api_key_id: str) -> ApiKey:
        """Enable API key"""
        api_key = await self.get_api_key_by_id(api_key_id)
        api_key.enable()
        return await self.api_key_dal.update(api_key)

    async def record_api_key_usage(self, key_hash: str) -> ApiKey:
        """Record API key usage"""
        api_key = await self.get_api_key_by_hash(key_hash)
        api_key.record_usage()
        return await self.api_key_dal.update(api_key)

    async def validate_api_key(self, plain_key: str) -> Optional[ApiKey]:
        """Validate API key and return if valid"""
        try:
            key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
            api_key = await self.get_api_key_by_hash(key_hash)

            if api_key.is_active():
                # Record usage
                await self.record_api_key_usage(key_hash)
                return api_key

            return None
        except NotFoundException:
            return None

    async def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get project statistics"""
        project = await self.get_project_by_id(project_id)
        api_key_count = await self.api_key_dal.count_by_project(project_id)
        active_keys = await self.api_key_dal.get_active_keys_by_project(project_id)

        return {
            "project_id": project_id,
            "project_name": project.name,
            "status": project.status.value,
            "total_api_keys": api_key_count,
            "active_api_keys": len(active_keys),
            "created_at": project.created_at,
            "last_updated": project.updated_at,
        }

    async def get_all_projects(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[Project]:
        """Get all projects across all organizations with pagination for admin"""

        if status and search:
            # Complex filtering
            projects = await self.project_dal.get_by_status(status)
            if search:
                projects = [proj for proj in projects if search.lower() in proj.name.lower()]
            total = len(projects)
            start = skip
            end = start + limit
            items = projects[start:end]
        elif status:
            projects = await self.project_dal.get_by_status(status)
            total = len(projects)
            start = skip
            end = start + limit
            items = projects[start:end]
        elif search:
            items = await self.project_dal.search_by_name(search)
            total = len(items)
            start = skip
            end = start + limit
            items = items[start:end]
        else:
            # Get all projects with pagination
            items = await self.project_dal.get_all_projects(skip, limit)
            total = await self.project_dal.count_all_projects()

        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit

        return PaginatedResponse[Project](
            items=items,
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def get_project_stats_admin(self) -> Dict[str, Any]:
        """Get project statistics for admin dashboard"""
        total_count = await self.project_dal.count_all_projects()
        active_count = await self.project_dal.count_by_status_all(ProjectStatus.ACTIVE)
        archived_count = await self.project_dal.count_by_status_all(ProjectStatus.ARCHIVED)

        return {
            "total_count": total_count,
            "active_count": active_count,
            "archived_count": archived_count,
        }
