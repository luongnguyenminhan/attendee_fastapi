from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.base_model import APIResponse
from app.exceptions.handlers import handle_exceptions
from app.modules.users.repository.user_repo import UserRepo
from app.modules.users.schemas import (
    CreateUserRequest,
    LoginRequest,
    ChangePasswordRequest,
    LoginDetailResponse,
    LoginResponse,
    UserResponse,
    UserProfileResponse,
)
from app.middlewares.translation_manager import _
from app.utils.security import create_access_token

route = APIRouter(prefix="/auth", tags=["authentication"])


@route.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
@handle_exceptions
async def register_user(
    request: CreateUserRequest, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Register a new user"""
    user_data = request.dict()
    user = await repo.create_user(user_data)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_registered_successfully")
    )


@route.post("/login", response_model=APIResponse[LoginResponse])
@handle_exceptions
async def login_user(
    request: LoginRequest, repo: UserRepo = Depends()
) -> APIResponse[LoginResponse]:
    """Login user with email/username and password"""
    # Authenticate user
    user = await repo.authenticate_user(request.identifier, request.password)

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "organization_id": (
                str(user.organization_id) if user.organization_id else None
            ),
        }
    )

    # Create response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfileResponse.from_orm(user),
    )

    return APIResponse.success(data=login_response, message=_("login_successful"))


@route.post("/change-password", response_model=APIResponse[None])
@handle_exceptions
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: UUID,  # This would come from JWT token in real implementation
    repo: UserRepo = Depends(),
) -> APIResponse[None]:
    """Change user password"""
    await repo.change_password(
        current_user_id, request.current_password, request.new_password
    )

    return APIResponse.success(message=_("password_changed_successfully"))


@route.get("/me", response_model=APIResponse[UserProfileResponse])
@handle_exceptions
async def get_current_user(
    current_user_id: UUID,  # This would come from JWT token in real implementation
    repo: UserRepo = Depends(),
) -> APIResponse[UserProfileResponse]:
    """Get current user profile"""
    user = await repo.get_user_by_id(current_user_id)

    return APIResponse.success(
        data=UserProfileResponse.from_orm(user), message=_("success")
    )


@route.post("/refresh", response_model=APIResponse[LoginResponse])
@handle_exceptions
async def refresh_token(
    current_user_id: UUID,  # This would come from refresh token in real implementation
    repo: UserRepo = Depends(),
) -> APIResponse[LoginResponse]:
    """Refresh access token"""
    user = await repo.get_user_by_id(current_user_id)

    # Create new access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "organization_id": (
                str(user.organization_id) if user.organization_id else None
            ),
        }
    )

    # Create response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfileResponse.from_orm(user),
    )

    return APIResponse.success(
        data=login_response, message=_("token_refreshed_successfully")
    )


@route.post("/logout", response_model=APIResponse[None])
@handle_exceptions
async def logout_user(
    current_user_id: UUID,  # This would come from JWT token in real implementation
) -> APIResponse[None]:
    """Logout user (invalidate token)"""
    # In a real implementation, you would invalidate the token
    # For now, just return success

    return APIResponse.success(message=_("logout_successful"))
