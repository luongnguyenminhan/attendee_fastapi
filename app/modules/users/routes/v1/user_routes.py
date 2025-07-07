from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.base_model import APIResponse, PaginatedResponse, PagingInfo
from app.exceptions.handlers import handle_exceptions
from app.modules.users.repository.user_repo import UserRepo
from app.modules.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    SearchUserRequest,
    UserDetailResponse,
    UserListResponse,
    UserProfileDetailResponse,
    UserResponse,
    UserProfileResponse,
)
from app.middlewares.translation_manager import _

route = APIRouter(prefix="/users", tags=["users"])


@route.post(
    "/", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED
)
@handle_exceptions
async def create_user(
    request: CreateUserRequest, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Create a new user"""
    user_data = request.dict()
    user = await repo.create_user(user_data)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_created_successfully")
    )


@route.get("/", response_model=APIResponse[PaginatedResponse[UserResponse]])
@handle_exceptions
async def get_users(
    request: SearchUserRequest = Depends(), repo: UserRepo = Depends()
) -> APIResponse[PaginatedResponse[UserResponse]]:
    """Get paginated list of users with optional search and filters"""

    skip = (request.page - 1) * request.page_size

    if request.query:
        users = await repo.search_users(request.query, skip, request.page_size)
        total_count = len(users)  # Simplified for demo
    else:
        users = await repo.get_active_users(skip, request.page_size)
        total_count = len(users)  # Simplified for demo

    # Convert to response models
    user_responses = [UserResponse.from_orm(user) for user in users]

    # Calculate pagination info
    total_pages = (total_count + request.page_size - 1) // request.page_size

    paging_info = PagingInfo(
        total=total_count,
        total_pages=total_pages,
        page=request.page,
        page_size=request.page_size,
    )

    paginated_response = PaginatedResponse(items=user_responses, paging=paging_info)

    return APIResponse.success(data=paginated_response, message=_("success"))


@route.get("/{user_id}", response_model=APIResponse[UserResponse])
@handle_exceptions
async def get_user_by_id(
    user_id: UUID, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Get user by ID"""
    user = await repo.get_user_by_id(user_id)

    return APIResponse.success(data=UserResponse.from_orm(user), message=_("success"))


@route.put("/{user_id}", response_model=APIResponse[UserResponse])
@handle_exceptions
async def update_user(
    user_id: UUID, request: UpdateUserRequest, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Update user information"""
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    user = await repo.update_user(user_id, update_data)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_updated_successfully")
    )


@route.delete("/{user_id}", response_model=APIResponse[None])
@handle_exceptions
async def delete_user(user_id: UUID, repo: UserRepo = Depends()) -> APIResponse[None]:
    """Delete user (soft delete)"""
    await repo.delete_user(user_id)

    return APIResponse.success(message=_("user_deleted_successfully"))


@route.post("/{user_id}/activate", response_model=APIResponse[UserResponse])
@handle_exceptions
async def activate_user(
    user_id: UUID, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Activate user account"""
    user = await repo.activate_user(user_id)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_activated_successfully")
    )


@route.post("/{user_id}/deactivate", response_model=APIResponse[UserResponse])
@handle_exceptions
async def deactivate_user(
    user_id: UUID, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Deactivate user account"""
    user = await repo.deactivate_user(user_id)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_deactivated_successfully")
    )


@route.post("/{user_id}/suspend", response_model=APIResponse[UserResponse])
@handle_exceptions
async def suspend_user(
    user_id: UUID, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Suspend user account"""
    user = await repo.suspend_user(user_id)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("user_suspended_successfully")
    )


@route.post("/{user_id}/verify-email", response_model=APIResponse[UserResponse])
@handle_exceptions
async def verify_user_email(
    user_id: UUID, repo: UserRepo = Depends()
) -> APIResponse[UserResponse]:
    """Verify user email"""
    user = await repo.verify_user_email(user_id)

    return APIResponse.success(
        data=UserResponse.from_orm(user), message=_("email_verified_successfully")
    )


@route.get(
    "/organization/{organization_id}",
    response_model=APIResponse[PaginatedResponse[UserResponse]],
)
@handle_exceptions
async def get_users_by_organization(
    organization_id: UUID,
    page: int = 1,
    page_size: int = 10,
    repo: UserRepo = Depends(),
) -> APIResponse[PaginatedResponse[UserResponse]]:
    """Get users by organization"""
    skip = (page - 1) * page_size
    users = await repo.get_users_by_organization(organization_id, skip, page_size)

    # Convert to response models
    user_responses = [UserResponse.from_orm(user) for user in users]

    # Calculate pagination info (simplified)
    total_count = len(users)
    total_pages = (total_count + page_size - 1) // page_size

    paging_info = PagingInfo(
        total=total_count, total_pages=total_pages, page=page, page_size=page_size
    )

    paginated_response = PaginatedResponse(items=user_responses, paging=paging_info)

    return APIResponse.success(data=paginated_response, message=_("success"))
