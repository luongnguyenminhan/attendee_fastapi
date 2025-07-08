import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.bots.repository.bot_repo import BotRepo
from app.modules.organizations.repository.organization_repo import OrganizationRepo
from app.modules.projects.repository.project_repo import ProjectRepo
from app.modules.users.repository.user_repo import UserRepo


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


router = APIRouter(prefix="/admin", tags=["Admin - System"])


@router.get("/dashboard", summary="Admin - Get dashboard statistics")
@handle_exceptions
async def admin_dashboard(
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin dashboard with comprehensive statistics and recent activity"""

    print("=== ADMIN DASHBOARD REQUEST ===")
    print(f"Admin user: {current_user}")
    print("================================")

    try:
        # Initialize repositories
        user_repo = UserRepo(db)
        org_repo = OrganizationRepo(db)
        project_repo = ProjectRepo(db)
        bot_repo = BotRepo(db)

        print("=== GATHERING DASHBOARD STATS ===")

        # Get stats from repositories in parallel
        print("1. Getting user stats...")
        user_stats = {
            "total_users": await user_repo.count_total_users(),
            "active_users": await user_repo.count_active_users(),
        }
        print(f"   - Total users: {user_stats['total_users']}")
        print(f"   - Active users: {user_stats['active_users']}")

        print("2. Getting organization stats...")
        org_stats = await org_repo.get_organization_stats()
        print(f"   - Total organizations: {org_stats.get('total_count', 0)}")
        print(f"   - Active organizations: {org_stats.get('active_count', 0)}")

        print("3. Getting project stats...")
        project_stats = await project_repo.get_project_stats_admin()
        print(f"   - Total projects: {project_stats.get('total_count', 0)}")
        print(f"   - Active projects: {project_stats.get('active_count', 0)}")

        print("4. Getting bot stats...")
        bot_stats = await bot_repo.get_bot_stats_admin()
        print(f"   - Total bots: {bot_stats.get('total_count', 0)}")
        print(f"   - Active bots: {bot_stats.get('joined_count', 0)}")

        # Combine all stats
        dashboard_stats = {
            "total_users": user_stats["total_users"],
            "active_users": user_stats["active_users"],
            "total_organizations": org_stats.get("total_count", 0),
            "active_organizations": org_stats.get("active_count", 0),
            "total_projects": project_stats.get("total_count", 0),
            "active_projects": project_stats.get("active_count", 0),
            "total_bots": bot_stats.get("total_count", 0),
            "active_bots": bot_stats.get("joined_count", 0),
            # Mock additional stats for now
            "webhook_deliveries": 0,
            "transcriptions": 0,
            "celery_workers": 0,
            "active_pods": 0,
        }

        print("✅ Dashboard stats compiled successfully")
        print("🎉 SUCCESS: Returning dashboard data")
        print("===================================")

        return JSONResponse(content={"success": True, "data": dashboard_stats}, status_code=200)

    except Exception as e:
        print(f"❌ DASHBOARD ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get dashboard stats: {str(e)}",
            },
            status_code=500,
        )


@router.get("/settings", summary="Admin - Get system settings")
@handle_exceptions
async def admin_get_settings(
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get system settings"""

    print("=== ADMIN GET SETTINGS ===")
    print(f"Admin user: {current_user}")
    print("===========================")

    try:
        # Mock system settings for now
        settings = {
            "system": {
                "maintenance_mode": False,
                "registration_enabled": True,
                "email_verification_required": True,
                "max_users_per_organization": 100,
                "default_credits": 1000,
            },
            "webhooks": {
                "enabled": True,
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "batch_size": 100,
            },
            "bots": {
                "max_concurrent_bots": 10,
                "default_recording_duration": 3600,
                "auto_leave_timeout": 7200,
            },
            "transcription": {
                "default_provider": "deepgram",
                "language": "en",
                "real_time": True,
            },
        }

        print("✅ System settings retrieved")
        return JSONResponse(content={"success": True, "data": settings}, status_code=200)

    except Exception as e:
        print(f"❌ GET SETTINGS ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to get settings: {str(e)}"},
            status_code=500,
        )


@router.get("/webhooks", summary="Admin - Get webhook deliveries")
@handle_exceptions
async def admin_get_webhooks(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get webhook delivery information"""

    print("=== ADMIN GET WEBHOOKS ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Status filter: {status}")
    print(f"Admin user: {current_user}")
    print("===========================")

    try:
        # Mock webhook deliveries for now
        mock_webhooks = [
            {
                "id": "webhook-1",
                "url": "https://example.com/webhook",
                "event_type": "bot.joined",
                "status": "delivered",
                "attempts": 1,
                "last_attempt": "2024-01-01T12:00:00Z",
                "response_code": 200,
                "response_time_ms": 150,
            },
            {
                "id": "webhook-2",
                "url": "https://example.com/webhook",
                "event_type": "bot.left",
                "status": "failed",
                "attempts": 3,
                "last_attempt": "2024-01-01T11:30:00Z",
                "response_code": 500,
                "response_time_ms": 5000,
            },
        ]

        response_data = {
            "webhooks": mock_webhooks,
            "total": len(mock_webhooks),
            "page": page,
            "page_size": page_size,
            "total_pages": 1,
        }

        print(f"✅ Webhook deliveries retrieved: {len(mock_webhooks)}")
        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ GET WEBHOOKS ERROR: {str(e)}")
        return JSONResponse(content={"error": f"Failed to get webhooks: {str(e)}"}, status_code=500)


@router.get("/transcriptions", summary="Admin - Get transcription information")
@handle_exceptions
async def admin_get_transcriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get transcription information"""

    print("=== ADMIN GET TRANSCRIPTIONS ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Admin user: {current_user}")
    print("=================================")

    try:
        # Mock transcriptions for now
        mock_transcriptions = [
            {
                "id": "trans-1",
                "bot_id": "bot-1",
                "duration_seconds": 3600,
                "word_count": 1500,
                "language": "en",
                "provider": "deepgram",
                "status": "completed",
                "created_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T11:00:00Z",
            },
            {
                "id": "trans-2",
                "bot_id": "bot-2",
                "duration_seconds": 1800,
                "word_count": 750,
                "language": "en",
                "provider": "deepgram",
                "status": "processing",
                "created_at": "2024-01-01T11:30:00Z",
                "completed_at": None,
            },
        ]

        response_data = {
            "transcriptions": mock_transcriptions,
            "total": len(mock_transcriptions),
            "page": page,
            "page_size": page_size,
            "total_pages": 1,
        }

        print(f"✅ Transcriptions retrieved: {len(mock_transcriptions)}")
        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ GET TRANSCRIPTIONS ERROR: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to get transcriptions: {str(e)}"},
            status_code=500,
        )


@router.get("/health", summary="Admin - System health check")
@handle_exceptions
async def admin_system_health(
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint for comprehensive system health check"""

    print("=== ADMIN SYSTEM HEALTH ===")
    print(f"Admin user: {current_user}")
    print("============================")

    try:
        # Mock health check data
        health_data = {
            "database": {
                "status": "healthy",
                "response_time_ms": 25,
                "connections": 5,
                "max_connections": 100,
            },
            "redis": {
                "status": "healthy",
                "response_time_ms": 5,
                "memory_usage_mb": 45,
                "max_memory_mb": 512,
            },
            "celery": {
                "status": "healthy",
                "active_workers": 2,
                "pending_tasks": 0,
                "failed_tasks": 0,
            },
            "storage": {
                "status": "healthy",
                "disk_usage_gb": 25,
                "disk_total_gb": 100,
            },
        }

        print("✅ System health check completed")
        return JSONResponse(content={"success": True, "data": health_data}, status_code=200)

    except Exception as e:
        print(f"❌ HEALTH CHECK ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Health check failed: {str(e)}"},
            status_code=500,
        )
