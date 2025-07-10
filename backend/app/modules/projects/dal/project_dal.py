from typing import List, Optional

from sqlmodel import func, select

from app.core.base_dal import BaseDAL
from app.modules.projects.models.project_model import (
    ApiKey,
    ApiKeyStatus,
    Project,
    ProjectStatus,
)


class ProjectDAL(BaseDAL[Project]):
    """Project Data Access Layer"""

    def __init__(self):
        super().__init__(Project)

    async def get_by_object_id(self, object_id: str) -> Optional[Project]:
        """Get project by object_id"""
        query = select(self.model).where(self.model.object_id == object_id, ~self.model.is_deleted)
        return await self._get_first(query)

    async def get_by_organization_id(self, organization_id: str) -> List[Project]:
        """Get projects by organization ID"""
        query = select(self.model).where(self.model.organization_id == organization_id, ~self.model.is_deleted).order_by(self.model.created_at.desc())
        return await self._get_all(query)

    async def get_by_organization_and_name(self, organization_id: str, name: str) -> Optional[Project]:
        """Get project by organization and name"""
        query = select(self.model).where(
            self.model.organization_id == organization_id,
            self.model.name == name,
            ~self.model.is_deleted,
        )
        return await self._get_first(query)

    async def search_by_name(self, name_pattern: str, organization_id: Optional[str] = None) -> List[Project]:
        """Search projects by name pattern"""
        query = select(self.model).where(self.model.name.ilike(f"%{name_pattern}%"), ~self.model.is_deleted)

        if organization_id:
            query = query.where(self.model.organization_id == organization_id)

        return await self._get_all(query.order_by(self.model.name))

    async def get_by_status(self, status: ProjectStatus, organization_id: Optional[str] = None) -> List[Project]:
        """Get projects by status"""
        query = select(self.model).where(self.model.status == status, ~self.model.is_deleted)

        if organization_id:
            query = query.where(self.model.organization_id == organization_id)

        return await self._get_all(query.order_by(self.model.created_at.desc()))

    async def count_by_organization(self, organization_id: str) -> int:
        """Count projects by organization"""
        query = select(func.count(self.model.id)).where(self.model.organization_id == organization_id, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def get_active_projects(self, organization_id: Optional[str] = None) -> List[Project]:
        """Get all active projects"""
        return await self.get_by_status(ProjectStatus.ACTIVE, organization_id)

    async def get_all_projects(self, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get all projects with pagination"""
        query = select(self.model).where(~self.model.is_deleted).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        return await self._get_all(query)

    async def count_all_projects(self) -> int:
        """Count all projects"""
        query = select(func.count(self.model.id)).where(~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def count_by_status_all(self, status: ProjectStatus) -> int:
        """Count projects by status across all organizations"""
        query = select(func.count(self.model.id)).where(self.model.status == status, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0


class ApiKeyDAL(BaseDAL[ApiKey]):
    """API Key Data Access Layer"""

    def __init__(self):
        super().__init__(ApiKey)

    async def get_by_object_id(self, object_id: str) -> Optional[ApiKey]:
        """Get API key by object_id"""
        query = select(self.model).where(self.model.object_id == object_id, ~self.model.is_deleted)
        return await self._get_first(query)

    async def get_by_key_hash(self, key_hash: str) -> Optional[ApiKey]:
        """Get API key by key hash"""
        query = select(self.model).where(self.model.key_hash == key_hash, ~self.model.is_deleted)
        return await self._get_first(query)

    async def get_by_project_id(self, project_id: str) -> List[ApiKey]:
        """Get API keys by project ID"""
        query = select(self.model).where(self.model.project_id == project_id, ~self.model.is_deleted).order_by(self.model.created_at.desc())
        return await self._get_all(query)

    async def get_active_keys_by_project(self, project_id: str) -> List[ApiKey]:
        """Get active API keys by project"""
        query = (
            select(self.model)
            .where(
                self.model.project_id == project_id,
                self.model.status == ApiKeyStatus.ACTIVE,
                ~self.model.is_deleted,
            )
            .order_by(self.model.created_at.desc())
        )
        return await self._get_all(query)

    async def get_by_status(self, status: ApiKeyStatus) -> List[ApiKey]:
        """Get API keys by status"""
        query = select(self.model).where(self.model.status == status, ~self.model.is_deleted).order_by(self.model.created_at.desc())
        return await self._get_all(query)

    async def count_by_project(self, project_id: str) -> int:
        """Count API keys by project"""
        query = select(func.count(self.model.id)).where(self.model.project_id == project_id, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def search_by_name(self, name_pattern: str, project_id: Optional[str] = None) -> List[ApiKey]:
        """Search API keys by name pattern"""
        query = select(self.model).where(self.model.name.ilike(f"%{name_pattern}%"), ~self.model.is_deleted)

        if project_id:
            query = query.where(self.model.project_id == project_id)

        return await self._get_all(query.order_by(self.model.name))

    async def get_expired_keys(self) -> List[ApiKey]:
        """Get expired API keys"""
        current_time = self.model.get_current_time()
        query = select(self.model).where(
            self.model.expires_at <= current_time,
            self.model.status != ApiKeyStatus.EXPIRED,
            ~self.model.is_deleted,
        )
        return await self._get_all(query)

    async def bulk_disable_by_project(self, project_id: str) -> bool:
        """Bulk disable all API keys for a project"""
        try:
            await self._begin_transaction()

            api_keys = await self.get_by_project_id(project_id)
            for api_key in api_keys:
                if api_key.status == ApiKeyStatus.ACTIVE:
                    api_key.disable()
                    await self.update(api_key)

            await self._commit_transaction()
            return True
        except Exception:
            await self._rollback_transaction()
            return False
