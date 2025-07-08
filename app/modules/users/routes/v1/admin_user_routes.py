import asyncio
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.core.database import get_session
from app.exceptions.exception import ConflictException, ValidationException
from app.exceptions.handlers import handle_exceptions
from app.modules.users.models.user_model import User, UserRole, UserStatus
from app.modules.users.repository.user_repo import UserRepo
from app.utils.security import get_password_hash


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

    def add(self, instance):
        """Direct wrapper for add (sync method)"""
        return self._session.add(instance)

    def delete(self, instance):
        """Direct wrapper for delete (sync method)"""
        return self._session.delete(instance)


async def get_async_session():
    """Get async-compatible session for admin routes"""
    async for session in get_session():
        yield AsyncSessionWrapper(session)


# Dependency to get current admin user (simplified for now)
async def get_current_admin_user():
    return {"username": "admin", "email": "admin@attendee.dev", "is_admin": True}


router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("/", summary="Admin - Get all users with advanced filtering")
@handle_exceptions
async def admin_get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    role_filter: str = Query(None, alias="role"),
    organization_id: str = Query(None),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get paginated users with comprehensive filtering and logging"""

    print("=== ADMIN GET USERS REQUEST ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Search: {search}")
    print(f"Status filter: {status_filter}")
    print(f"Role filter: {role_filter}")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("================================")

    try:
        repo = UserRepo(db)

        print("=== FILTERING USERS ===")
        if search:
            print(f"Searching users with query: '{search}'")
            users = await repo.search_users(search, (page - 1) * page_size, page_size)
            total_count = await repo.count_search_users(search)
        else:
            print("Getting all users with filters")
            users = await repo.get_active_users((page - 1) * page_size, page_size)
            total_count = await repo.count_total_users()

        print(f"✅ Found {len(users)} users (total: {total_count})")

        # Convert to response format
        user_responses = []
        for user in users:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_email_verified": user.is_email_verified,
                "status": "active" if user.is_active else "inactive",
                "role": "admin" if user.is_superuser else "user",
                "organization_id": (str(user.organization_id) if user.organization_id else None),
                "created_at": (user.create_date.isoformat() if user.create_date else None),
                "updated_at": (user.update_date.isoformat() if user.update_date else None),
            }
            user_responses.append(user_data)

        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size

        response_data = {
            "users": user_responses,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

        print(f"✅ Response prepared with {len(user_responses)} users")
        print("🎉 SUCCESS: Returning admin users list")
        print("========================================")

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ ADMIN GET USERS ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return JSONResponse(content={"error": f"Failed to get users: {str(e)}"}, status_code=500)


@router.post("/create", summary="Admin - Create new user")
@handle_exceptions
async def admin_create_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    first_name: Optional[str] = Form(""),
    last_name: Optional[str] = Form(""),
    role: str = Form("user"),
    organization_id: Optional[str] = Form(None),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to create new user with comprehensive logging"""

    # Log incoming request
    print("=== ADMIN CREATE USER REQUEST ===")
    print(f"Email: {email}")
    print(f"Username: {username}")
    print(f"Password length: {len(password) if password else 0}")
    print(f"First name: {first_name}")
    print(f"Last name: {last_name}")
    print(f"Role: {role}")
    print(f"Organization ID: {organization_id}")
    print(f"Current user: {current_user}")
    print("==================================")

    try:
        # Validate input data
        email_clean = email.strip()
        username_clean = username.strip()

        print("=== VALIDATION STEP ===")
        print(f"Email cleaned: '{email_clean}'")
        print(f"Username cleaned: '{username_clean}'")
        print(f"Password provided: {bool(password)}")
        print("=======================")

        if not email_clean or not username_clean or not password:
            print("❌ VALIDATION FAILED: Required fields missing")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Required fields missing",
                },
                status_code=400,
            )

        # Check for existing email
        print("=== CHECKING EMAIL UNIQUENESS ===")
        result = await db.execute(select(User).filter(User.email == email_clean))
        existing_email = result.scalar_one_or_none()
        print(f"Email '{email_clean}' exists: {bool(existing_email)}")
        if existing_email:
            print(f"❌ EMAIL CONFLICT: User ID {existing_email.id}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Email already exists",
                },
                status_code=409,
            )

        # Check for existing username
        print("=== CHECKING USERNAME UNIQUENESS ===")
        result = await db.execute(select(User).filter(User.username == username_clean))
        existing_username = result.scalar_one_or_none()
        print(f"Username '{username_clean}' exists: {bool(existing_username)}")
        if existing_username:
            print(f"❌ USERNAME CONFLICT: User ID {existing_username.id}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Username already exists",
                },
                status_code=409,
            )

        # Prepare organization ID if provided
        print("=== PROCESSING ORGANIZATION ID ===")
        org_id = None
        if organization_id and organization_id.strip():
            try:
                from uuid import UUID

                org_id = UUID(organization_id.strip())
                print(f"✅ Organization ID parsed: {org_id}")
            except ValueError as e:
                print(f"❌ INVALID ORG ID: '{organization_id}' - {e}")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Invalid organization ID format",
                    },
                    status_code=400,
                )
        else:
            print("No organization ID provided")

        # Hash password
        print("=== HASHING PASSWORD ===")
        hashed_password = get_password_hash(password)
        print(f"✅ Password hashed: {len(hashed_password)} chars")

        # Create user object
        print("=== CREATING USER OBJECT ===")
        is_admin = role == "admin"
        print(f"Creating user with role: {role} (is_admin: {is_admin})")

        new_user = User(
            email=email_clean,
            username=username_clean,
            hashed_password=hashed_password,
            first_name=first_name.strip() if first_name else "",
            last_name=last_name.strip() if last_name else "",
            status=UserStatus.ACTIVE,
            role=UserRole.USER,
            is_active=True,
            is_email_verified=False,
            is_superuser=is_admin,
            organization_id=org_id,
        )
        print("✅ User object created:")
        print(f"   - Email: {new_user.email}")
        print(f"   - Username: {new_user.username}")
        print(f"   - First name: {new_user.first_name}")
        print(f"   - Last name: {new_user.last_name}")
        print(f"   - Is superuser: {new_user.is_superuser}")
        print(f"   - Organization ID: {new_user.organization_id}")

        # Add to database
        print("=== DATABASE OPERATIONS ===")
        print("1. Adding user to session...")
        db.add(new_user)
        print("2. Flushing to get ID...")
        await db.flush()
        print("3. Refreshing user object...")
        await db.refresh(new_user)
        print(f"   - Generated User ID: {new_user.id}")
        print("4. Committing transaction...")
        await db.commit()
        print("✅ User created successfully in database")

        # Prepare response data
        print("=== PREPARING RESPONSE ===")
        response_data = {
            "id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username,
            "first_name": new_user.first_name or "",
            "last_name": new_user.last_name or "",
            "full_name": f"{new_user.first_name or ''} {new_user.last_name or ''}".strip(),
            "status": "active" if new_user.is_active else "inactive",
            "role": "admin" if new_user.is_superuser else "user",
            "is_email_verified": new_user.is_email_verified,
            "is_superuser": new_user.is_superuser,
            "organization_id": (str(new_user.organization_id) if new_user.organization_id else None),
            "create_date": (new_user.create_date.isoformat() if new_user.create_date else None),
            "update_date": (new_user.update_date.isoformat() if new_user.update_date else None),
        }

        print("✅ Response data prepared:")
        print(f"   - User ID: {response_data['id']}")
        print(f"   - Full name: {response_data['full_name']}")
        print(f"   - Role: {response_data['role']}")
        print(f"   - Status: {response_data['status']}")
        print(f"   - Created: {response_data['create_date']}")

        final_response = {
            "success": True,
            "message": f"User '{username}' created successfully!",
            "data": response_data,
        }

        print("🎉 SUCCESS: Returning 201 response")
        print("========================================")

        return JSONResponse(
            content=final_response,
            status_code=201,
        )

    except ValidationException as e:
        print(f"❌ VALIDATION EXCEPTION: {str(e)}")
        await db.rollback()
        print("🔄 Database rolled back")
        return JSONResponse(
            content={
                "success": False,
                "message": str(e),
            },
            status_code=400,
        )
    except ConflictException as e:
        print(f"❌ CONFLICT EXCEPTION: {str(e)}")
        await db.rollback()
        print("🔄 Database rolled back")
        return JSONResponse(
            content={
                "success": False,
                "message": str(e),
            },
            status_code=409,
        )
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        print("📍 Error details:")
        import traceback

        traceback.print_exc()
        await db.rollback()
        print("🔄 Database rolled back")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
            },
            status_code=500,
        )


@router.get("/{user_id}", summary="Admin - Get user details")
@handle_exceptions
async def admin_get_user_details(
    user_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get detailed user information"""

    print("=== ADMIN GET USER DETAILS ===")
    print(f"User ID: {user_id}")
    print(f"Admin user: {current_user}")
    print("===============================")

    try:
        repo = UserRepo(db)
        user = await repo.get_user_by_id(UUID(user_id))

        if not user:
            print(f"❌ USER NOT FOUND: {user_id}")
            return JSONResponse(content={"success": False, "message": "User not found"}, status_code=404)

        user_data = {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_email_verified": user.is_email_verified,
            "status": "active" if user.is_active else "inactive",
            "role": "admin" if user.is_superuser else "user",
            "organization_id": (str(user.organization_id) if user.organization_id else None),
            "created_at": user.create_date.isoformat() if user.create_date else None,
            "updated_at": user.update_date.isoformat() if user.update_date else None,
        }

        print(f"✅ User details retrieved: {user.email}")
        return JSONResponse(content={"success": True, "data": user_data}, status_code=200)

    except Exception as e:
        print(f"❌ GET USER DETAILS ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to get user: {str(e)}"},
            status_code=500,
        )


@router.post("/{user_id}/activate", summary="Admin - Activate user")
@handle_exceptions
async def admin_activate_user(
    user_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to activate user account"""

    print("=== ADMIN ACTIVATE USER ===")
    print(f"User ID: {user_id}")
    print(f"Admin user: {current_user}")
    print("============================")

    try:
        repo = UserRepo(db)
        user = await repo.activate_user(UUID(user_id))

        print(f"✅ User activated: {user.email}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"User {user.email} activated successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ ACTIVATE USER ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to activate user: {str(e)}"},
            status_code=500,
        )


@router.post("/{user_id}/deactivate", summary="Admin - Deactivate user")
@handle_exceptions
async def admin_deactivate_user(
    user_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to deactivate user account"""

    print("=== ADMIN DEACTIVATE USER ===")
    print(f"User ID: {user_id}")
    print(f"Admin user: {current_user}")
    print("==============================")

    try:
        repo = UserRepo(db)
        user = await repo.deactivate_user(UUID(user_id))

        print(f"✅ User deactivated: {user.email}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"User {user.email} deactivated successfully",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ DEACTIVATE USER ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to deactivate user: {str(e)}",
            },
            status_code=500,
        )


@router.delete("/{user_id}", summary="Admin - Delete user")
@handle_exceptions
async def admin_delete_user(
    user_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to delete user (soft delete)"""

    print("=== ADMIN DELETE USER ===")
    print(f"User ID: {user_id}")
    print(f"Admin user: {current_user}")
    print("==========================")

    try:
        repo = UserRepo(db)
        await repo.delete_user(UUID(user_id))

        print(f"✅ User deleted: {user_id}")
        return JSONResponse(
            content={"success": True, "message": "User deleted successfully"},
            status_code=200,
        )

    except Exception as e:
        print(f"❌ DELETE USER ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to delete user: {str(e)}"},
            status_code=500,
        )
