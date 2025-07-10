import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.projects.repository.project_repo import ProjectRepo


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


router = APIRouter(prefix="/admin/projects", tags=["Admin - Projects"])


@router.get("/", summary="Admin - Get all projects with advanced filtering")
@handle_exceptions
async def admin_get_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    organization_id: str = Query(None),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get paginated projects with comprehensive filtering and logging"""

    print("=== ADMIN GET PROJECTS REQUEST ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Search: {search}")
    print(f"Status filter: {status_filter}")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("===================================")

    try:
        repo = ProjectRepo(db)
        skip = (page - 1) * page_size

        print("=== FILTERING PROJECTS ===")
        if organization_id:
            print(f"Getting projects for organization: {organization_id}")
            projects_page = await repo.get_projects_by_organization(
                organization_id=organization_id,
                skip=skip,
                limit=page_size,
                status=status_filter,
                search=search,
            )
        else:
            print("Getting all projects with filters")
            projects_page = await repo.get_all_projects_admin(
                skip=skip,
                limit=page_size,
                status=status_filter,
                search=search,
            )

        print(f"✅ Found {len(projects_page.items)} projects (total: {projects_page.total})")

        # Convert to response format
        project_responses = []
        for project in projects_page.items:
            project_data = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "organization_id": (str(project.organization_id) if project.organization_id else None),
                "settings": project.settings,
                "status": project.status,
                "created_at": (project.create_date.isoformat() if project.create_date else None),
                "updated_at": (project.update_date.isoformat() if project.update_date else None),
            }
            project_responses.append(project_data)

        response_data = {
            "projects": project_responses,
            "total": projects_page.total,
            "page": page,
            "page_size": page_size,
            "total_pages": projects_page.total_pages,
        }

        print(f"✅ Response prepared with {len(project_responses)} projects")
        print("🎉 SUCCESS: Returning admin projects list")
        print("==========================================")

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ ADMIN GET PROJECTS ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return JSONResponse(content={"error": f"Failed to get projects: {str(e)}"}, status_code=500)


@router.get("/stats", summary="Admin - Get project statistics")
@handle_exceptions
async def admin_get_project_stats(
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get comprehensive project statistics"""

    print("=== ADMIN GET PROJECT STATS ===")
    print(f"Admin user: {current_user}")
    print("================================")

    try:
        repo = ProjectRepo(db)
        stats = await repo.get_project_stats_admin()

        print("✅ Project stats retrieved:")
        print(f"   - Total projects: {stats.get('total_count', 0)}")
        print(f"   - Active projects: {stats.get('active_count', 0)}")
        print(f"   - Archived projects: {stats.get('archived_count', 0)}")

        return JSONResponse(content={"success": True, "data": stats}, status_code=200)

    except Exception as e:
        print(f"❌ GET PROJECT STATS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get project stats: {str(e)}",
            },
            status_code=500,
        )


@router.get("/{project_id}", summary="Admin - Get project details")
@handle_exceptions
async def admin_get_project_details(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get detailed project information"""

    print("=== ADMIN GET PROJECT DETAILS ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("==================================")

    try:
        repo = ProjectRepo(db)
        project = await repo.get_project_by_id(project_id)

        if not project:
            print(f"❌ PROJECT NOT FOUND: {project_id}")
            return JSONResponse(
                content={"success": False, "message": "Project not found"},
                status_code=404,
            )

        project_data = {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "organization_id": (str(project.organization_id) if project.organization_id else None),
            "settings": project.settings,
            "status": project.status,
            "created_at": (project.create_date.isoformat() if project.create_date else None),
            "updated_at": (project.update_date.isoformat() if project.update_date else None),
        }

        print(f"✅ Project details retrieved: {project.name}")
        return JSONResponse(content={"success": True, "data": project_data}, status_code=200)

    except Exception as e:
        print(f"❌ GET PROJECT DETAILS ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to get project: {str(e)}"},
            status_code=500,
        )


@router.get("/{project_id}/stats", summary="Admin - Get project statistics")
@handle_exceptions
async def admin_get_project_individual_stats(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get individual project statistics"""

    print("=== ADMIN GET PROJECT INDIVIDUAL STATS ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("===========================================")

    try:
        repo = ProjectRepo(db)
        stats = await repo.get_project_stats(project_id)

        print("✅ Project individual stats retrieved")
        return JSONResponse(content={"success": True, "data": stats}, status_code=200)

    except Exception as e:
        print(f"❌ GET PROJECT INDIVIDUAL STATS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get project stats: {str(e)}",
            },
            status_code=500,
        )


@router.post("/{project_id}/archive", summary="Admin - Archive project")
@handle_exceptions
async def admin_archive_project(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to archive project"""

    print("=== ADMIN ARCHIVE PROJECT ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("==============================")

    try:
        repo = ProjectRepo(db)
        project = await repo.archive_project(project_id)

        print(f"✅ Project archived: {project.name}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Project {project.name} archived successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ ARCHIVE PROJECT ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to archive project: {str(e)}",
            },
            status_code=500,
        )


@router.post("/{project_id}/activate", summary="Admin - Activate project")
@handle_exceptions
async def admin_activate_project(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to activate project"""

    print("=== ADMIN ACTIVATE PROJECT ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("===============================")

    try:
        repo = ProjectRepo(db)
        project = await repo.activate_project(project_id)

        print(f"✅ Project activated: {project.name}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Project {project.name} activated successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ ACTIVATE PROJECT ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to activate project: {str(e)}",
            },
            status_code=500,
        )


@router.delete("/{project_id}", summary="Admin - Delete project")
@handle_exceptions
async def admin_delete_project(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to delete project (soft delete)"""

    print("=== ADMIN DELETE PROJECT ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("=============================")

    try:
        repo = ProjectRepo(db)
        await repo.delete_project(project_id)

        print(f"✅ Project deleted: {project_id}")
        return JSONResponse(
            content={"success": True, "message": "Project deleted successfully"},
            status_code=200,
        )

    except Exception as e:
        print(f"❌ DELETE PROJECT ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to delete project: {str(e)}",
            },
            status_code=500,
        )


@router.get("/{project_id}/api-keys", summary="Admin - Get project API keys")
@handle_exceptions
async def admin_get_project_api_keys(
    project_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get project API keys"""

    print("=== ADMIN GET PROJECT API KEYS ===")
    print(f"Project ID: {project_id}")
    print(f"Admin user: {current_user}")
    print("===================================")

    try:
        repo = ProjectRepo(db)
        api_keys = await repo.get_project_api_keys(project_id)

        print(f"✅ Found {len(api_keys)} API keys for project")
        return JSONResponse(
            content={
                "success": True,
                "data": {"api_keys": api_keys, "total": len(api_keys)},
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ GET PROJECT API KEYS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get project API keys: {str(e)}",
            },
            status_code=500,
        )
