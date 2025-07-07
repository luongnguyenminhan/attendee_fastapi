from typing import Optional, List
from sqlmodel import select, func

from app.core.base_dal import BaseDAL
from app.modules.organizations.models.organization_model import (
    Organization,
    OrganizationStatus,
)


class OrganizationDAL(BaseDAL[Organization]):
    """Organization Data Access Layer"""

    def __init__(self):
        super().__init__(Organization)

    async def get_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        query = select(self.model).where(
            self.model.name == name, ~self.model.is_deleted
        )
        return await self._get_first(query)

    async def search_by_name(self, name_pattern: str) -> List[Organization]:
        """Search organizations by name pattern"""
        query = (
            select(self.model)
            .where(self.model.name.ilike(f"%{name_pattern}%"), ~self.model.is_deleted)
            .order_by(self.model.name)
        )
        return await self._get_all(query)

    async def get_by_status(self, status: OrganizationStatus) -> List[Organization]:
        """Get organizations by status"""
        query = (
            select(self.model)
            .where(self.model.status == status, ~self.model.is_deleted)
            .order_by(self.model.created_at.desc())
        )
        return await self._get_all(query)

    async def get_active_organizations(self) -> List[Organization]:
        """Get all active organizations"""
        return await self.get_by_status(OrganizationStatus.ACTIVE)

    async def get_with_low_credits(self, threshold: int = 100) -> List[Organization]:
        """Get organizations with credits below threshold"""
        query = (
            select(self.model)
            .where(
                self.model.centicredits < threshold,
                self.model.status == OrganizationStatus.ACTIVE,
                ~self.model.is_deleted,
            )
            .order_by(self.model.centicredits)
        )
        return await self._get_all(query)

    async def get_webhook_enabled_organizations(self) -> List[Organization]:
        """Get organizations with webhooks enabled"""
        query = (
            select(self.model)
            .where(
                self.model.is_webhooks_enabled.is_(True),
                self.model.status == OrganizationStatus.ACTIVE,
                ~self.model.is_deleted,
            )
            .order_by(self.model.name)
        )
        return await self._get_all(query)

    async def get_total_credits(self) -> int:
        """Get total credits across all active organizations"""
        query = select(func.sum(self.model.centicredits)).where(
            self.model.status == OrganizationStatus.ACTIVE, ~self.model.is_deleted
        )
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def count_by_status(self, status: OrganizationStatus) -> int:
        """Count organizations by status"""
        query = select(func.count(self.model.id)).where(
            self.model.status == status, ~self.model.is_deleted
        )
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def bulk_update_status(
        self, organization_ids: List[str], status: OrganizationStatus
    ) -> bool:
        """Bulk update status for multiple organizations"""
        try:
            await self._begin_transaction()

            for org_id in organization_ids:
                organization = await self.get_by_id(org_id)
                if organization:
                    organization.status = status
                    await self.update(organization)

            await self._commit_transaction()
            return True
        except Exception:
            await self._rollback_transaction()
            return False
