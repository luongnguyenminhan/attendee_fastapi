import asyncio

from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.organizations.repository.organization_repo import OrganizationRepo


class AsyncSessionWrapper:
    """Wrapper to make sync session compatible with async repository interface"""

    def __init__(self, sync_session: Session):
        self._session = sync_session

    def __getattr__(self, name):
        """Delegate all attributes to the wrapped session"""
        attr = getattr(self._session, name)
        if name == "execute":
            return self._async_execute
        return attr

    async def _async_execute(self, statement):
        """Convert sync execute to async"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.execute, statement)

    async def commit(self):
        """Async wrapper for commit"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.commit)

    async def rollback(self):
        """Async wrapper for rollback"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.rollback)

    async def close(self):
        """Async wrapper for close"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.close)

    async def flush(self):
        """Async wrapper for flush"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.flush)

    async def refresh(self, instance):
        """Async wrapper for refresh"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.refresh, instance)


async def get_async_session():
    """Get async-compatible session for admin routes"""
    async for session in get_session():
        yield AsyncSessionWrapper(session)


# Dependency to get current admin user (simplified for now)
async def get_current_admin_user():
    return {"username": "admin", "email": "admin@attendee.dev", "is_admin": True}


router = APIRouter(prefix="/admin/organizations", tags=["Admin - Organizations"])


@router.get("/", summary="Admin - Get all organizations with advanced filtering")
@handle_exceptions
async def admin_get_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get paginated organizations with comprehensive filtering and logging"""

    print("=== ADMIN GET ORGANIZATIONS REQUEST ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Search: {search}")
    print(f"Status filter: {status_filter}")
    print(f"Admin user: {current_user}")
    print("========================================")

    try:
        repo = OrganizationRepo(db)
        skip = (page - 1) * page_size

        print("=== FILTERING ORGANIZATIONS ===")
        organizations_page = await repo.get_organizations(skip=skip, limit=page_size, status=status_filter, search=search)

        print(f"✅ Found {len(organizations_page.items)} organizations (total: {organizations_page.total})")

        # Convert to response format
        org_responses = []
        for org in organizations_page.items:
            org_data = {
                "id": str(org.id),
                "name": org.name,
                "centicredits": org.centicredits,
                "is_webhooks_enabled": org.is_webhooks_enabled,
                "version": org.version,
                "settings": org.settings,
                "created_at": org.create_date.isoformat() if org.create_date else None,
                "updated_at": org.update_date.isoformat() if org.update_date else None,
            }
            org_responses.append(org_data)

        response_data = {
            "organizations": org_responses,
            "total": organizations_page.total,
            "page": page,
            "page_size": page_size,
            "total_pages": organizations_page.total_pages,
        }

        print(f"✅ Response prepared with {len(org_responses)} organizations")
        print("🎉 SUCCESS: Returning admin organizations list")
        print("===============================================")

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ ADMIN GET ORGANIZATIONS ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return JSONResponse(content={"error": f"Failed to get organizations: {str(e)}"}, status_code=500)


@router.get("/stats", summary="Admin - Get organization statistics")
@handle_exceptions
async def admin_get_organization_stats(
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get comprehensive organization statistics"""

    print("=== ADMIN GET ORGANIZATION STATS ===")
    print(f"Admin user: {current_user}")
    print("=====================================")

    try:
        repo = OrganizationRepo(db)
        stats = await repo.get_organization_stats()

        print("✅ Organization stats retrieved:")
        print(f"   - Total organizations: {stats.get('total_count', 0)}")
        print(f"   - Active organizations: {stats.get('active_count', 0)}")

        return JSONResponse(content={"success": True, "data": stats}, status_code=200)

    except Exception as e:
        print(f"❌ GET ORGANIZATION STATS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get organization stats: {str(e)}",
            },
            status_code=500,
        )


@router.get("/low-credits", summary="Admin - Get organizations with low credits")
@handle_exceptions
async def admin_get_low_credit_organizations(
    threshold: int = Query(100, ge=0, description="Credit threshold"),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get organizations with low credits"""

    print("=== ADMIN GET LOW CREDIT ORGS ===")
    print(f"Threshold: {threshold}")
    print(f"Admin user: {current_user}")
    print("==================================")

    try:
        repo = OrganizationRepo(db)
        organizations = await repo.get_low_credit_organizations(threshold)

        print(f"✅ Found {len(organizations.items)} organizations with low credits")
        return JSONResponse(content={"success": True, "data": organizations}, status_code=200)

    except Exception as e:
        print(f"❌ GET LOW CREDIT ORGS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get low credit organizations: {str(e)}",
            },
            status_code=500,
        )


@router.get("/{organization_id}", summary="Admin - Get organization details")
@handle_exceptions
async def admin_get_organization_details(
    organization_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get detailed organization information"""

    print("=== ADMIN GET ORGANIZATION DETAILS ===")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("=======================================")

    try:
        repo = OrganizationRepo(db)
        organization = await repo.get_organization_by_id(organization_id)

        if not organization:
            print(f"❌ ORGANIZATION NOT FOUND: {organization_id}")
            return JSONResponse(
                content={"success": False, "message": "Organization not found"},
                status_code=404,
            )

        org_data = {
            "id": str(organization.id),
            "name": organization.name,
            "centicredits": organization.centicredits,
            "is_webhooks_enabled": organization.is_webhooks_enabled,
            "version": organization.version,
            "settings": organization.settings,
            "created_at": (organization.create_date.isoformat() if organization.create_date else None),
            "updated_at": (organization.update_date.isoformat() if organization.update_date else None),
        }

        print(f"✅ Organization details retrieved: {organization.name}")
        return JSONResponse(content={"success": True, "data": org_data}, status_code=200)

    except Exception as e:
        print(f"❌ GET ORGANIZATION DETAILS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get organization: {str(e)}",
            },
            status_code=500,
        )


@router.post("/{organization_id}/credits", summary="Admin - Manage organization credits")
@handle_exceptions
async def admin_manage_organization_credits(
    organization_id: str,
    amount: int = Form(...),
    operation: str = Form(...),  # "add" or "deduct"
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to manage organization credits"""

    print("=== ADMIN MANAGE CREDITS ===")
    print(f"Organization ID: {organization_id}")
    print(f"Amount: {amount}")
    print(f"Operation: {operation}")
    print(f"Admin user: {current_user}")
    print("=============================")

    try:
        repo = OrganizationRepo(db)

        # Get current credits before operation
        org_before = await repo.get_organization_by_id(organization_id)
        old_credits = org_before.centicredits

        # Perform operation
        organization = await repo.manage_credits(
            organization_id=organization_id,
            amount=amount,
            operation=operation,
        )

        print(f"✅ Credits updated: {old_credits} -> {organization.centicredits}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Credits {operation}ed successfully",
                "data": {
                    "organization_id": organization_id,
                    "old_credits": old_credits,
                    "new_credits": organization.centicredits,
                    "amount_changed": amount,
                    "operation": operation,
                },
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ MANAGE CREDITS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to manage credits: {str(e)}",
            },
            status_code=500,
        )


@router.post("/{organization_id}/suspend", summary="Admin - Suspend organization")
@handle_exceptions
async def admin_suspend_organization(
    organization_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to suspend organization"""

    print("=== ADMIN SUSPEND ORGANIZATION ===")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("===================================")

    try:
        repo = OrganizationRepo(db)
        organization = await repo.suspend_organization(organization_id)

        print(f"✅ Organization suspended: {organization.name}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Organization {organization.name} suspended successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ SUSPEND ORGANIZATION ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to suspend organization: {str(e)}",
            },
            status_code=500,
        )


@router.post("/{organization_id}/activate", summary="Admin - Activate organization")
@handle_exceptions
async def admin_activate_organization(
    organization_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to activate organization"""

    print("=== ADMIN ACTIVATE ORGANIZATION ===")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("====================================")

    try:
        repo = OrganizationRepo(db)
        organization = await repo.activate_organization(organization_id)

        print(f"✅ Organization activated: {organization.name}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Organization {organization.name} activated successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ ACTIVATE ORGANIZATION ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to activate organization: {str(e)}",
            },
            status_code=500,
        )


@router.delete("/{organization_id}", summary="Admin - Delete organization")
@handle_exceptions
async def admin_delete_organization(
    organization_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to delete organization (soft delete)"""

    print("=== ADMIN DELETE ORGANIZATION ===")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("==================================")

    try:
        repo = OrganizationRepo(db)
        await repo.delete_organization(organization_id)

        print(f"✅ Organization deleted: {organization_id}")
        return JSONResponse(
            content={"success": True, "message": "Organization deleted successfully"},
            status_code=200,
        )

    except Exception as e:
        print(f"❌ DELETE ORGANIZATION ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to delete organization: {str(e)}",
            },
            status_code=500,
        )
