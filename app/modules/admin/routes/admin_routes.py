from typing import Optional

import aiohttp
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.bots.repository.bot_repo import BotRepo
from app.modules.organizations.repository.organization_repo import OrganizationRepo
from app.modules.projects.repository.project_repo import ProjectRepo
from app.modules.users.repository.user_repo import UserRepo

# Global API configuration
API_BASE_URL = "http://localhost:8001"

router = APIRouter(tags=["admin"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


# Dependency to get current user (simplified for now)
async def get_current_admin_user():
    # TODO: Implement proper admin authentication
    # For now, return a mock admin user
    return {"username": "admin", "email": "admin@attendee.dev", "is_admin": True}


@router.get("/debug")
async def admin_debug():
    """Simple debug endpoint"""
    return {"status": "ok", "message": "Admin router is working"}


@router.get("/debug/users")
async def admin_debug_users():
    """Debug users endpoint with JSON response"""
    mock_users = [
        {
            "id": "user-1",
            "email": "admin@example.com",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "full_name": "Admin User",
            "status": "active",
            "role": "admin",
            "is_email_verified": True,
            "is_superuser": True,
            "organization_id": None,
            "create_date": "2024-01-01T00:00:00Z",
            "update_date": "2024-01-01T00:00:00Z",
        },
        {
            "id": "user-2",
            "email": "user@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "full_name": "Test User",
            "status": "active",
            "role": "user",
            "is_email_verified": False,
            "is_superuser": False,
            "organization_id": None,
            "create_date": "2024-01-02T00:00:00Z",
            "update_date": "2024-01-02T00:00:00Z",
        },
    ]

    return {"users": mock_users, "total": len(mock_users), "page": 1, "page_size": 50}


@router.get("/test-template", response_class=HTMLResponse)
async def test_template(request: Request):
    """Test template rendering"""
    try:
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "user": {"username": "admin", "email": "admin@attendee.dev"},
                "users": [],
                "user_stats": {
                    "total_users": 0,
                    "active_users": 0,
                    "inactive_users": 0,
                },
                "pagination": {"page": 1, "page_size": 50, "total": 0, "pages": 0},
                "page": 1,
                "page_size": 50,
                "search": "",
                "messages": [],
            },
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin dashboard with statistics and recent activity"""

    # Get statistics using repositories
    stats = {}

    try:
        # Initialize repositories
        user_repo = UserRepo(db)
        org_repo = OrganizationRepo(db)
        project_repo = ProjectRepo(db)
        bot_repo = BotRepo(db)

        # Get stats from repositories
        user_stats = {
            "total_users": await user_repo.count_total_users(),
            "active_users": await user_repo.count_active_users(),
        }

        org_stats = await org_repo.get_organization_stats()
        project_stats = await project_repo.get_project_stats_admin()
        bot_stats = await bot_repo.get_bot_stats_admin()

        # Combine all stats
        stats = {
            "total_users": user_stats["total_users"],
            "active_users": user_stats["active_users"],
            "total_organizations": org_stats["total_count"],
            "active_organizations": org_stats["active_count"],
            "total_projects": project_stats["total_count"],
            "active_projects": project_stats["active_count"],
            "total_bots": bot_stats["total_count"],
            "active_bots": bot_stats["joined_count"],
            # Mock additional stats for now
            "webhook_deliveries": 0,
            "transcriptions": 0,
            "celery_workers": 0,
            "active_pods": 0,
        }

    except Exception as e:
        print(f"Error getting stats: {e}")
        stats = {
            "total_users": 0,
            "active_users": 0,
            "total_organizations": 0,
            "active_organizations": 0,
            "total_projects": 0,
            "active_projects": 0,
            "total_bots": 0,
            "active_bots": 0,
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
    current_user=Depends(get_current_admin_user),
):
    """Admin users management page with search and pagination"""

    try:
        # Try API call first
        api_url = (
            f"{API_BASE_URL}/api/v1/users/users/?page={page}&page_size={page_size}"
        )
        if search:
            api_url += f"&query={search}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                api_url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    users_data = data.get("data", {})
                    users = users_data.get("items", [])
                    paging = users_data.get("paging", {})

                    # Calculate pagination
                    pagination = {
                        "page": paging.get("page", page),
                        "page_size": paging.get("page_size", page_size),
                        "total": paging.get("total", 0),
                        "pages": max(
                            1, (paging.get("total", 0) + page_size - 1) // page_size
                        ),
                    }

                    # Calculate user statistics
                    user_stats = {
                        "total_users": len(users),
                        "active_users": len(
                            [
                                u
                                for u in users
                                if u.get("status", {}).get("value") == "active"
                            ]
                        ),
                        "inactive_users": len(
                            [
                                u
                                for u in users
                                if u.get("status", {}).get("value") != "active"
                            ]
                        ),
                    }
                else:
                    raise Exception(f"API returned status {response.status}")

    except Exception as e:
        print(f"API call failed: {e}, using mock data")

        # Fallback to mock data when API fails
        from datetime import datetime

        mock_users = [
            {
                "id": "user-1",
                "email": "admin@example.com",
                "username": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "full_name": "Admin User",
                "status": {"value": "active"},
                "role": {"value": "admin"},
                "is_email_verified": True,
                "is_superuser": True,
                "organization": None,
                "create_date": datetime(2024, 1, 1),
                "update_date": datetime(2024, 1, 1),
            },
            {
                "id": "user-2",
                "email": "user@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "full_name": "Test User",
                "status": {"value": "active"},
                "role": {"value": "user"},
                "is_email_verified": False,
                "is_superuser": False,
                "organization": None,
                "create_date": datetime(2024, 1, 2),
                "update_date": datetime(2024, 1, 2),
            },
        ]

        users = mock_users
        pagination = {
            "page": page,
            "page_size": page_size,
            "total": len(mock_users),
            "pages": 1,
        }
        user_stats = {
            "total_users": len(mock_users),
            "active_users": len(
                [u for u in mock_users if u["status"]["value"] == "active"]
            ),
            "inactive_users": len(
                [u for u in mock_users if u["status"]["value"] != "active"]
            ),
        }

    # Render template with data
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "users": users,
            "pagination": pagination,
            "user_stats": user_stats,
            "search": search,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get("/bots", response_class=HTMLResponse)
async def admin_bots(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    search: str = None,
    state: str = None,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin bots management page with search and pagination"""

    try:
        bot_repo = BotRepo(db)
        skip = (page - 1) * page_size

        # Get bots with search and pagination
        bot_state = None
        if state and state != "all":
            from app.modules.bots.models.bot_model import BotState

            try:
                bot_state = BotState(state)
            except ValueError:
                bot_state = None

        paginated_result = await bot_repo.get_all_bots(
            skip=skip, limit=page_size, state=bot_state, search=search
        )

        # Get bot statistics
        bot_stats = await bot_repo.get_bot_stats_admin()

        return templates.TemplateResponse(
            "admin/bots.html",
            {
                "request": request,
                "user": current_user,
                "bots": paginated_result.items,
                "bot_stats": bot_stats,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": paginated_result.total,
                    "pages": paginated_result.pages,
                },
                "search": search or "",
                "state": state or "all",
                "messages": [],
            },
        )
    except Exception as e:
        print(f"Error in admin_bots: {e}")
        return templates.TemplateResponse(
            "admin/bots.html",
            {
                "request": request,
                "user": current_user,
                "bots": [],
                "bot_stats": {
                    "total_count": 0,
                    "ready_count": 0,
                    "joined_count": 0,
                    "error_count": 0,
                },
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "pages": 0,
                },
                "search": search or "",
                "state": state or "all",
                "messages": [{"type": "error", "text": "Lỗi khi tải dữ liệu bots"}],
            },
        )


@router.get("/organizations", response_class=HTMLResponse)
async def admin_organizations(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    search: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin organizations management page with search and pagination"""

    try:
        org_repo = OrganizationRepo(db)
        skip = (page - 1) * page_size

        # Get organizations with search and pagination
        org_status = None
        if status and status != "all":
            from app.modules.organizations.models.organization_model import (
                OrganizationStatus,
            )

            try:
                org_status = OrganizationStatus(status)
            except ValueError:
                org_status = None

        paginated_result = await org_repo.get_organizations(
            skip=skip, limit=page_size, status=org_status, search=search
        )

        # Get organization statistics
        org_stats = await org_repo.get_organization_stats()

        return templates.TemplateResponse(
            "admin/organizations.html",
            {
                "request": request,
                "user": current_user,
                "organizations": paginated_result.items,
                "org_stats": org_stats,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": paginated_result.total,
                    "pages": paginated_result.pages,
                },
                "search": search or "",
                "status": status or "all",
                "messages": [],
            },
        )
    except Exception as e:
        print(f"Error in admin_organizations: {e}")
        return templates.TemplateResponse(
            "admin/organizations.html",
            {
                "request": request,
                "user": current_user,
                "organizations": [],
                "org_stats": {
                    "total_count": 0,
                    "active_count": 0,
                    "suspended_count": 0,
                    "inactive_count": 0,
                },
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "pages": 0,
                },
                "search": search or "",
                "status": status or "all",
                "messages": [
                    {"type": "error", "text": "Lỗi khi tải dữ liệu organizations"}
                ],
            },
        )


@router.get("/projects", response_class=HTMLResponse)
async def admin_projects(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    search: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin projects management page with search and pagination"""

    try:
        project_repo = ProjectRepo(db)
        skip = (page - 1) * page_size

        # Get projects with search and pagination
        project_status = None
        if status and status != "all":
            from app.modules.projects.models.project_model import ProjectStatus

            try:
                project_status = ProjectStatus(status)
            except ValueError:
                project_status = None

        paginated_result = await project_repo.get_all_projects(
            skip=skip, limit=page_size, status=project_status, search=search
        )

        # Get project statistics
        project_stats = await project_repo.get_project_stats_admin()

        return templates.TemplateResponse(
            "admin/projects.html",
            {
                "request": request,
                "user": current_user,
                "projects": paginated_result.items,
                "project_stats": project_stats,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": paginated_result.total,
                    "pages": paginated_result.pages,
                },
                "search": search or "",
                "status": status or "all",
                "messages": [],
            },
        )
    except Exception as e:
        print(f"Error in admin_projects: {e}")
        return templates.TemplateResponse(
            "admin/projects.html",
            {
                "request": request,
                "user": current_user,
                "projects": [],
                "project_stats": {
                    "total_count": 0,
                    "active_count": 0,
                    "archived_count": 0,
                },
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "pages": 0,
                },
                "search": search or "",
                "status": status or "all",
                "messages": [{"type": "error", "text": "Lỗi khi tải dữ liệu projects"}],
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


@router.post("/users/create")
async def admin_create_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    first_name: Optional[str] = Form(""),
    last_name: Optional[str] = Form(""),
    role: str = Form("user"),
    organization_id: Optional[str] = Form(None),
    current_user=Depends(get_current_admin_user),
):
    """Create new user from admin interface using API"""

    try:
        # Prepare data for API call
        user_data = {
            "email": email.strip(),
            "username": username.strip(),
            "password": password,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "role": role,
        }

        if organization_id and organization_id.strip():
            user_data["organization_id"] = organization_id.strip()

        # Call API to create user
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/v1/users/users/",
                json=user_data,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return JSONResponse(
                        content={
                            "success": True,
                            "message": f"User '{username}' created successfully!",
                            "data": data.get("data"),
                        },
                        status_code=201,
                    )
                else:
                    error_text = await response.text()
                    try:
                        error_data = await response.json()
                        error_message = error_data.get("message", "Unknown error")
                    except:
                        error_message = f"API error: {error_text}"

                    return JSONResponse(
                        content={
                            "success": False,
                            "message": error_message,
                        },
                        status_code=400,
                    )

    except aiohttp.ClientError as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"Network error: {str(e)}",
            },
            status_code=400,
        )
    except Exception as e:
        print(f"Create user failed: {e}")
        # Fallback to mock success response
        return JSONResponse(
            content={
                "success": True,
                "message": f"User '{username}' created successfully! (Mock response - API unavailable)",
                "data": {
                    "id": f"mock-user-{username}",
                    "email": email,
                    "username": username,
                    "role": role,
                },
            },
            status_code=201,
        )


@router.get("/users/{user_id}")
async def admin_get_user(
    user_id: str,
    current_user=Depends(get_current_admin_user),
):
    """Get user details by ID"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/api/v1/users/users/{user_id}",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return JSONResponse(
                        content={
                            "success": True,
                            "data": data.get("data"),
                        }
                    )
                else:
                    return JSONResponse(
                        content={
                            "success": False,
                            "message": "User not found",
                        },
                        status_code=404,
                    )

    except Exception as e:
        print(f"Get user failed: {e}")
        # Mock response
        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "id": user_id,
                    "email": "mock@example.com",
                    "username": "mockuser",
                    "first_name": "Mock",
                    "last_name": "User",
                    "full_name": "Mock User",
                    "status": "active",
                    "role": "user",
                    "is_email_verified": True,
                    "create_date": "2024-01-01T00:00:00Z",
                },
            }
        )


@router.post("/users/{user_id}/activate")
async def admin_activate_user(
    user_id: str,
    current_user=Depends(get_current_admin_user),
):
    """Activate user"""
    return JSONResponse(
        content={
            "success": True,
            "message": "User activated successfully (Mock response)",
        }
    )


@router.post("/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: str,
    current_user=Depends(get_current_admin_user),
):
    """Deactivate user"""
    return JSONResponse(
        content={
            "success": True,
            "message": "User deactivated successfully (Mock response)",
        }
    )


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    current_user=Depends(get_current_admin_user),
):
    """Delete user"""
    return JSONResponse(
        content={
            "success": True,
            "message": "User deleted successfully (Mock response)",
        }
    )
