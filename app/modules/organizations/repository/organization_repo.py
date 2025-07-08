from typing import Any, Dict, List, Optional

from sqlmodel import Session

from app.core.base_model import PaginatedResponse
from app.exceptions.exception import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.modules.organizations.dal.organization_dal import OrganizationDAL
from app.modules.organizations.models.organization_model import (
    Organization,
    OrganizationStatus,
)


class OrganizationRepo:
    """Organization Repository - Business Logic Layer"""

    def __init__(self, session: Session):
        self.session = session
        self.dal = OrganizationDAL()
        self.dal.set_session(session)

    async def create_organization(
        self,
        name: str,
        initial_credits: int = 500,
        enable_webhooks: bool = True,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Create new organization with validation"""
        # Validate input
        if not name or len(name.strip()) < 2:
            raise ValidationException("organizations.validation.name_too_short")

        if initial_credits < 0:
            raise ValidationException("organizations.validation.invalid_credits")

        # Check name uniqueness
        existing = await self.dal.get_by_name(name.strip())
        if existing:
            raise ConflictException("organizations.errors.name_already_exists")

        # Create organization
        organization = Organization(
            name=name.strip(),
            centicredits=initial_credits,
            is_webhooks_enabled=enable_webhooks,
            status=OrganizationStatus.ACTIVE,
            settings=settings or {},
        )

        return await self.dal.create(organization)

    async def get_organization_by_id(self, organization_id: str) -> Organization:
        """Get organization by ID with validation"""
        organization = await self.dal.get_by_id(organization_id)
        if not organization:
            raise NotFoundException("organizations.errors.not_found")
        return organization

    async def get_organization_by_name(self, name: str) -> Organization:
        """Get organization by name"""
        organization = await self.dal.get_by_name(name)
        if not organization:
            raise NotFoundException("organizations.errors.not_found")
        return organization

    async def update_organization(
        self,
        organization_id: str,
        name: Optional[str] = None,
        is_webhooks_enabled: Optional[bool] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Update organization with validation"""
        organization = await self.get_organization_by_id(organization_id)

        # Validate new name if provided
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ValidationException("organizations.validation.name_too_short")

            # Check name uniqueness
            if name.strip() != organization.name:
                existing = await self.dal.get_by_name(name.strip())
                if existing:
                    raise ConflictException("organizations.errors.name_already_exists")

            organization.name = name.strip()

        if is_webhooks_enabled is not None:
            organization.is_webhooks_enabled = is_webhooks_enabled

        if settings is not None:
            organization.settings = settings

        return await self.dal.update(organization)

    async def delete_organization(self, organization_id: str) -> bool:
        """Soft delete organization"""
        organization = await self.get_organization_by_id(organization_id)
        return await self.dal.delete(organization)

    async def get_organizations(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[OrganizationStatus] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[Organization]:
        """Get paginated organizations with filters"""

        if status and search:
            # Complex filtering - get by status first then filter by search
            organizations = await self.dal.get_by_status(status)
            if search:
                organizations = [org for org in organizations if search.lower() in org.name.lower()]
            total = len(organizations)
            start = skip
            end = start + limit
            items = organizations[start:end]
        elif status:
            organizations = await self.dal.get_by_status(status)
            total = len(organizations)
            start = skip
            end = start + limit
            items = organizations[start:end]
        elif search:
            items = await self.dal.search_by_name(search)
            total = len(items)
            start = skip
            end = start + limit
            items = items[start:end]
        else:
            items, total = await self.dal.get_all_with_pagination(skip, limit)

        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit

        return PaginatedResponse[Organization](
            items=items,
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def manage_credits(self, organization_id: str, amount: int, operation: str = "add") -> Organization:
        """Add or deduct credits from organization"""
        organization = await self.get_organization_by_id(organization_id)

        if operation == "add":
            if amount <= 0:
                raise ValidationException("organizations.validation.invalid_credit_amount")
            organization.add_credits(amount)
        elif operation == "deduct":
            if amount <= 0:
                raise ValidationException("organizations.validation.invalid_credit_amount")
            if not organization.deduct_credits(amount):
                raise ValidationException("organizations.validation.insufficient_credits")
        else:
            raise ValidationException("organizations.validation.invalid_operation")

        return await self.dal.update(organization)

    async def suspend_organization(self, organization_id: str) -> Organization:
        """Suspend organization"""
        organization = await self.get_organization_by_id(organization_id)
        organization.suspend()
        return await self.dal.update(organization)

    async def activate_organization(self, organization_id: str) -> Organization:
        """Activate organization"""
        organization = await self.get_organization_by_id(organization_id)
        organization.activate()
        return await self.dal.update(organization)

    async def get_low_credit_organizations(self, threshold: int = 100) -> List[Organization]:
        """Get organizations with low credits"""
        return await self.dal.get_with_low_credits(threshold)

    async def get_organization_stats(self) -> Dict[str, Any]:
        """Get organization statistics"""
        # Temporarily disable status-based counting until migration
        # active_count = await self.dal.count_by_status(OrganizationStatus.ACTIVE)
        # suspended_count = await self.dal.count_by_status(OrganizationStatus.SUSPENDED)
        # inactive_count = await self.dal.count_by_status(OrganizationStatus.INACTIVE)

        # Get total count instead
        total_orgs, total_count = await self.dal.get_all_with_pagination(0, 1000)
        total_credits = await self.dal.get_total_credits()

        return {
            "total_count": total_count,
            "active_count": total_count,  # Assume all active for now
            "suspended_count": 0,
            "inactive_count": 0,
            "total_credits": total_credits,
        }
