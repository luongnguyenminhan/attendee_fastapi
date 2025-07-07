from typing import Optional
from uuid import UUID

from app.core.base_model import RequestSchema, FilterableRequestSchema
from app.modules.users.models.user_model import UserRole, UserStatus


class CreateUserRequest(RequestSchema):
    """Request schema for creating a new user"""

    email: str
    username: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    role: Optional[UserRole] = UserRole.USER
    organization_id: Optional[UUID] = None


class UpdateUserRequest(RequestSchema):
    """Request schema for updating user information"""

    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    organization_id: Optional[UUID] = None


class ChangePasswordRequest(RequestSchema):
    """Request schema for changing user password"""

    current_password: str
    new_password: str


class LoginRequest(RequestSchema):
    """Request schema for user login"""

    identifier: str  # email or username
    password: str


class SearchUserRequest(FilterableRequestSchema):
    """Request schema for searching users with pagination"""

    query: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    organization_id: Optional[UUID] = None


class UserStatusUpdateRequest(RequestSchema):
    """Request schema for updating user status"""

    status: UserStatus


class EmailVerificationRequest(RequestSchema):
    """Request schema for email verification"""

    email: str
    verification_code: str


class ResetPasswordRequest(RequestSchema):
    """Request schema for password reset"""

    email: str


class ConfirmResetPasswordRequest(RequestSchema):
    """Request schema for confirming password reset"""

    email: str
    reset_code: str
    new_password: str
