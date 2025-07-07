from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.base_model import PagingInfo
from app.exceptions.handlers import handle_exceptions
from app.modules.users.models.user_model import User
from app.modules.users.repository.user_repo import UserRepo
from app.modules.organizations.repository.organization_repo import OrganizationRepo
from app.modules.organizations.schemas.organization_request import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    ManageCreditsRequest,
    GetOrganizationsRequest,
    GetLowCreditOrganizationsRequest,
)
from app.modules.organizations.schemas.organization_response import (
    OrganizationAPIResponse,
    OrganizationResponse,
    OrganizationListResponse,
    OrganizationPaginatedAPIResponse,
    OrganizationStatsAPIResponse,
    OrganizationStatsResponse,
    CreditTransactionAPIResponse,
    CreditTransactionResponse,
)
from app.utils.security import get_current_user

router = APIRouter(tags=["Organizations"])


@router.post(
    "/",
    response_model=OrganizationAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
@handle_exceptions
async def create_organization(
    request: CreateOrganizationRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationAPIResponse:
    """Create a new organization"""
    repo = OrganizationRepo(session)

    organization = await repo.create_organization(
        name=request.name,
        initial_credits=request.initial_credits,
        enable_webhooks=request.enable_webhooks,
        settings=request.settings,
    )

    response_data = OrganizationResponse.from_entity(organization)
    return OrganizationAPIResponse.success(
        data=response_data, message="organizations.messages.created_successfully"
    )


@router.get(
    "/", response_model=OrganizationPaginatedAPIResponse, summary="Get organizations"
)
@handle_exceptions
async def get_organizations(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: str = Query(None, alias="status"),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> OrganizationPaginatedAPIResponse:
    """Get paginated list of organizations"""
    repo = OrganizationRepo(session)

    skip = (page - 1) * size

    organizations_page = await repo.get_organizations(
        skip=skip, limit=size, status=status_filter, search=search
    )

    # Convert entities to response schemas
    response_items = [
        OrganizationListResponse.from_entity(org) for org in organizations_page.items
    ]

    organizations_page.items = response_items

    return OrganizationPaginatedAPIResponse.success(
        data=organizations_page, message="organizations.messages.retrieved_successfully"
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationAPIResponse,
    summary="Get organization by ID",
)
@handle_exceptions
async def get_organization(
    organization_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationAPIResponse:
    """Get organization by ID"""
    repo = OrganizationRepo(session)

    organization = await repo.get_organization_by_id(organization_id)
    response_data = OrganizationResponse.from_entity(organization)

    return OrganizationAPIResponse.success(
        data=response_data, message="organizations.messages.retrieved_successfully"
    )


@router.patch(
    "/{organization_id}",
    response_model=OrganizationAPIResponse,
    summary="Update organization",
)
@handle_exceptions
async def update_organization(
    organization_id: str,
    request: UpdateOrganizationRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationAPIResponse:
    """Update organization"""
    repo = OrganizationRepo(session)

    organization = await repo.update_organization(
        organization_id=organization_id,
        name=request.name,
        is_webhooks_enabled=request.is_webhooks_enabled,
        settings=request.settings,
    )

    response_data = OrganizationResponse.from_entity(organization)
    return OrganizationAPIResponse.success(
        data=response_data, message="organizations.messages.updated_successfully"
    )


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization",
)
@handle_exceptions
async def delete_organization(
    organization_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete organization (soft delete)"""
    repo = OrganizationRepo(session)
    await repo.delete_organization(organization_id)


@router.post(
    "/{organization_id}/credits",
    response_model=CreditTransactionAPIResponse,
    summary="Manage organization credits",
)
@handle_exceptions
async def manage_credits(
    organization_id: str,
    request: ManageCreditsRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CreditTransactionAPIResponse:
    """Add or deduct credits from organization"""
    repo = OrganizationRepo(session)

    # Get current credits before operation
    org_before = await repo.get_organization_by_id(organization_id)
    old_credits = org_before.centicredits

    # Perform operation
    organization = await repo.manage_credits(
        organization_id=organization_id,
        amount=request.amount,
        operation=request.operation,
    )

    response_data = CreditTransactionResponse(
        organization_id=organization_id,
        old_credits=old_credits,
        new_credits=organization.centicredits,
        amount_changed=request.amount,
        operation=request.operation,
    )

    return CreditTransactionAPIResponse.success(
        data=response_data,
        message="organizations.messages.credits_updated_successfully",
    )


@router.post(
    "/{organization_id}/suspend",
    response_model=OrganizationAPIResponse,
    summary="Suspend organization",
)
@handle_exceptions
async def suspend_organization(
    organization_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationAPIResponse:
    """Suspend organization"""
    repo = OrganizationRepo(session)

    organization = await repo.suspend_organization(organization_id)
    response_data = OrganizationResponse.from_entity(organization)

    return OrganizationAPIResponse.success(
        data=response_data, message="organizations.messages.suspended_successfully"
    )


@router.post(
    "/{organization_id}/activate",
    response_model=OrganizationAPIResponse,
    summary="Activate organization",
)
@handle_exceptions
async def activate_organization(
    organization_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationAPIResponse:
    """Activate organization"""
    repo = OrganizationRepo(session)

    organization = await repo.activate_organization(organization_id)
    response_data = OrganizationResponse.from_entity(organization)

    return OrganizationAPIResponse.success(
        data=response_data, message="organizations.messages.activated_successfully"
    )


@router.get(
    "/stats/overview",
    response_model=OrganizationStatsAPIResponse,
    summary="Get organization statistics",
)
@handle_exceptions
async def get_organization_stats(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationStatsAPIResponse:
    """Get organization statistics"""
    repo = OrganizationRepo(session)

    stats = await repo.get_organization_stats()
    response_data = OrganizationStatsResponse(**stats)

    return OrganizationStatsAPIResponse.success(
        data=response_data,
        message="organizations.messages.stats_retrieved_successfully",
    )


@router.get(
    "/low-credits",
    response_model=OrganizationPaginatedAPIResponse,
    summary="Get organizations with low credits",
)
@handle_exceptions
async def get_low_credit_organizations(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    threshold: int = Query(100, ge=0, description="Credit threshold"),
) -> OrganizationPaginatedAPIResponse:
    """Get organizations with credits below threshold"""
    repo = OrganizationRepo(session)

    organizations = await repo.get_low_credit_organizations(threshold)

    response_items = [
        OrganizationListResponse.from_entity(org) for org in organizations
    ]

    # Create a simple paginated response for this endpoint
    paginated_response = {
        "items": response_items,
        "total": len(response_items),
        "page": 1,
        "size": len(response_items),
        "pages": 1,
    }

    return OrganizationPaginatedAPIResponse.success(
        data=paginated_response,
        message="organizations.messages.low_credits_retrieved_successfully",
    )
