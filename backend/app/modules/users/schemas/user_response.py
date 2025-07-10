from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict

from app.core.base_model import APIResponse, PaginatedResponse, ResponseSchema
from app.modules.users.models.user_model import UserRole, UserStatus


class UserResponse(ResponseSchema):
    """Response schema for user data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    status: UserStatus
    role: UserRole
    is_email_verified: bool
    is_superuser: bool
    organization_id: Optional[UUID]
    create_date: datetime
    update_date: datetime


class UserProfileResponse(ResponseSchema):
    """Response schema for user profile (limited data)"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    is_email_verified: bool
    organization_id: Optional[UUID]


class LoginResponse(ResponseSchema):
    """Response schema for login"""

    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse


class UserListResponse(APIResponse[PaginatedResponse[UserResponse]]):
    """Response schema for paginated user list"""

    pass


class UserDetailResponse(APIResponse[UserResponse]):
    """Response schema for single user detail"""

    pass


class UserProfileDetailResponse(APIResponse[UserProfileResponse]):
    """Response schema for user profile detail"""

    pass


class LoginDetailResponse(APIResponse[LoginResponse]):
    """Response schema for login detail"""

    pass


class MessageResponse(ResponseSchema):
    """Response schema for simple messages"""

    message: str
    success: bool = True


class UserStatsResponse(ResponseSchema):
    """Response schema for user statistics"""

    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    verified_users: int
    unverified_users: int
    users_by_role: dict


class UserStatsDetailResponse(APIResponse[UserStatsResponse]):
    """Response schema for user statistics detail"""

    pass
