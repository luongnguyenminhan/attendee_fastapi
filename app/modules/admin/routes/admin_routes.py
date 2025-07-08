from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_session
from app.modules.users.models.user_model import User
from app.modules.users.repository.user_repo import UserRepo
from app.modules.users.dependencies import get_user_repo
from app.modules.organizations.models.organization_model import Organization
from app.modules.projects.models.project_model import Project
from app.modules.bots.models.bot_model import Bot

router = APIRouter()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


# Dependency to get current user (simplified for now)
async def get_current_admin_user():
    # TODO: Implement proper admin authentication
    # For now, return a mock admin user
    return {"username": "admin", "email": "admin@attendee.dev", "is_admin": True}


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin dashboard with statistics and recent activity"""

    # Get basic statistics
    stats = {}

    try:
        # Count total users
        result = await db.execute(select(func.count(User.id)))
        stats["total_users"] = result.scalar() or 0

        # Count total organizations
        result = await db.execute(select(func.count(Organization.id)))
        stats["total_organizations"] = result.scalar() or 0

        # Count total projects
        result = await db.execute(select(func.count(Project.id)))
        stats["total_projects"] = result.scalar() or 0

        # Count total bots
        result = await db.execute(select(func.count(Bot.id)))
        stats["total_bots"] = result.scalar() or 0

        # Mock additional stats for now
        stats["webhook_deliveries"] = 0
        stats["transcriptions"] = 0
        stats["celery_workers"] = 0
        stats["active_pods"] = 0

    except Exception as e:
        print(f"Error getting stats: {e}")
        stats = {
            "total_users": 0,
            "total_bots": 0,
            "webhook_deliveries": 0,
            "transcriptions": 0,
            "celery_workers": 0,
            "active_pods": 0,
        }

    # Mock recent activities for now
    recent_activities = []

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "recent_activities": recent_activities,
            "messages": [],  # Flash messages
        },
    )


@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    search: str = None,
    user_repo: UserRepo = Depends(get_user_repo),
    current_user=Depends(get_current_admin_user),
):
    """Admin users management page with search and pagination"""

    try:
        skip = (page - 1) * page_size

        # Get users with optional search
        if search:
            users = await user_repo.search_users(search, skip, page_size)
        else:
            users = await user_repo.get_all_users(skip, page_size)

        # Get user statistics for dashboard
        total_users = await user_repo.count_total_users()
        active_users = await user_repo.count_active_users()

        user_stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
        }

        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "user": current_user,
                "users": users,
                "user_stats": user_stats,
                "page": page,
                "page_size": page_size,
                "search": search or "",
                "messages": [],
            },
        )
    except Exception as e:
        print(f"Error in admin_users: {e}")
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "user": current_user,
                "users": [],
                "user_stats": {
                    "total_users": 0,
                    "active_users": 0,
                    "inactive_users": 0,
                },
                "page": page,
                "page_size": page_size,
                "search": search or "",
                "messages": [{"type": "error", "text": "Lỗi khi tải dữ liệu users"}],
            },
        )


@router.get("/bots", response_class=HTMLResponse)
async def admin_bots(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin bots management page"""

    # Get all bots with their projects
    result = await db.execute(select(Bot).join(Project).join(Organization))
    bots = result.scalars().all()

    return templates.TemplateResponse(
        "admin/bots.html",
        {"request": request, "user": current_user, "bots": bots, "messages": []},
    )


@router.get("/organizations", response_class=HTMLResponse)
async def admin_organizations(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin organizations management page"""

    # Get all organizations
    result = await db.execute(select(Organization))
    organizations = result.scalars().all()

    return templates.TemplateResponse(
        "admin/organizations.html",
        {
            "request": request,
            "user": current_user,
            "organizations": organizations,
            "messages": [],
        },
    )


@router.get("/projects", response_class=HTMLResponse)
async def admin_projects(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin projects management page"""

    # Get all projects with organizations
    result = await db.execute(select(Project).join(Organization))
    projects = result.scalars().all()

    return templates.TemplateResponse(
        "admin/projects.html",
        {
            "request": request,
            "user": current_user,
            "projects": projects,
            "messages": [],
        },
    )


@router.get("/webhooks", response_class=HTMLResponse)
async def admin_webhooks(
    request: Request, current_user=Depends(get_current_admin_user)
):
    """Admin webhooks management page"""

    # TODO: Implement webhook statistics when webhook models are ready
    webhook_stats = {
        "total_subscriptions": 0,
        "successful_deliveries": 0,
        "failed_deliveries": 0,
        "pending_deliveries": 0,
    }

    return templates.TemplateResponse(
        "admin/webhooks.html",
        {
            "request": request,
            "user": current_user,
            "webhook_stats": webhook_stats,
            "messages": [],
        },
    )


@router.get("/transcriptions", response_class=HTMLResponse)
async def admin_transcriptions(
    request: Request, current_user=Depends(get_current_admin_user)
):
    """Admin transcriptions management page"""

    # TODO: Implement transcription statistics when transcription models are ready
    transcription_stats = {
        "total_transcriptions": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
    }

    return templates.TemplateResponse(
        "admin/transcriptions.html",
        {
            "request": request,
            "user": current_user,
            "transcription_stats": transcription_stats,
            "messages": [],
        },
    )


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(
    request: Request, current_user=Depends(get_current_admin_user)
):
    """Admin settings page"""

    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "user": current_user, "messages": []},
    )
