from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.base_model import APIResponse, RequestSchema
from app.exceptions.handlers import handle_exceptions
from app.middlewares.translation_manager import _
from app.modules.users.dependencies import get_user_repo
from app.modules.users.repository.user_repo import UserRepo
from app.modules.users.schemas import (
    ChangePasswordRequest,
    ConfirmResetPasswordRequest,
    CreateUserRequest,
    EmailVerificationRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    UserProfileResponse,
    UserResponse,
)
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
@handle_exceptions
async def register_user(request: CreateUserRequest, repo: UserRepo = Depends(get_user_repo)) -> APIResponse[UserResponse]:
    """Register a new user"""
    user_data = request.dict()
    user = await repo.create_user(user_data)

    return APIResponse.success(data=UserResponse.from_orm(user), message=_("user_registered_successfully"))


@router.post("/login", response_model=APIResponse[LoginResponse])
@handle_exceptions
async def login_user(request: LoginRequest, repo: UserRepo = Depends(get_user_repo)) -> APIResponse[LoginResponse]:
    """Login user with email/username and password"""
    # Authenticate user
    user = await repo.authenticate_user(request.identifier, request.password)

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "organization_id": (str(user.organization_id) if user.organization_id else None),
        }
    )

    # Create response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfileResponse.from_orm(user),
    )

    return APIResponse.success(data=login_response, message=_("login_successful"))


@router.post("/change-password", response_model=APIResponse[None])
@handle_exceptions
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: UUID,  # This would come from JWT token in real implementation
    repo: UserRepo = Depends(get_user_repo),
) -> APIResponse[None]:
    """Change user password"""
    await repo.change_password(current_user_id, request.current_password, request.new_password)

    return APIResponse.success(message=_("password_changed_successfully"))


@router.get("/me", response_model=APIResponse[UserProfileResponse])
@handle_exceptions
async def get_current_user(
    current_user_id: UUID,  # This would come from JWT token in real implementation
    repo: UserRepo = Depends(get_user_repo),
) -> APIResponse[UserProfileResponse]:
    """Get current user profile"""
    user = await repo.get_user_by_id(current_user_id)

    return APIResponse.success(data=UserProfileResponse.from_orm(user), message=_("success"))


@router.post("/refresh", response_model=APIResponse[LoginResponse])
@handle_exceptions
async def refresh_token(
    current_user_id: UUID,  # This would come from refresh token in real implementation
    repo: UserRepo = Depends(get_user_repo),
) -> APIResponse[LoginResponse]:
    """Refresh access token"""
    user = await repo.get_user_by_id(current_user_id)

    # Create new access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "organization_id": (str(user.organization_id) if user.organization_id else None),
        }
    )

    # Create response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfileResponse.from_orm(user),
    )

    return APIResponse.success(data=login_response, message=_("token_refreshed_successfully"))


@router.post("/logout", response_model=APIResponse[None])
@handle_exceptions
async def logout_user(
    current_user_id: UUID,  # This would come from JWT token in real implementation
) -> APIResponse[None]:
    """Logout user (invalidate token)"""
    # In a real implementation, you would invalidate the token
    # For now, just return success

    return APIResponse.success(message=_("logout_successful"))


@router.post("/password-reset", response_model=APIResponse[None])
@handle_exceptions
async def password_reset(request: ResetPasswordRequest, repo: UserRepo = Depends(get_user_repo), background_tasks: BackgroundTasks = None):
    """Send password reset email"""
    await repo.send_password_reset_email(request.email, background_tasks)
    return APIResponse.success(message=_("password_reset_email_sent"))


@router.post("/password-reset-confirm", response_model=APIResponse[None])
@handle_exceptions
async def password_reset_confirm(request: ConfirmResetPasswordRequest, repo: UserRepo = Depends(get_user_repo)):
    """Confirm password reset"""
    await repo.confirm_reset_password(request.email, request.reset_code, request.new_password)
    return APIResponse.success(message=_("password_reset_successful"))


@router.post("/resend-verification", response_model=APIResponse[None])
@handle_exceptions
async def resend_verification(request: ResetPasswordRequest, repo: UserRepo = Depends(get_user_repo), background_tasks: BackgroundTasks = None):
    """Resend verification email"""
    await repo.resend_verification_email(request.email, background_tasks)
    return APIResponse.success(message=_("verification_email_sent"))


@router.post("/email-verify", response_model=APIResponse[None])
@handle_exceptions
async def email_verify(request: EmailVerificationRequest, repo: UserRepo = Depends(get_user_repo)):
    """Verify email with code"""
    await repo.verify_email(request.email, request.verification_code)
    return APIResponse.success(message=_("email_verified_successful"))


class GoogleLoginRequest(RequestSchema):
    id_token: str


@router.post("/google", response_model=APIResponse[LoginResponse])
@handle_exceptions
async def google_login(request: GoogleLoginRequest, repo: UserRepo = Depends(get_user_repo)):
    """Login with Google OAuth"""
    user = await repo.login_with_google(request.id_token)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "organization_id": (str(user.organization_id) if user.organization_id else None),
        }
    )
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfileResponse.from_orm(user),
    )
    return APIResponse.success(data=login_response, message=_("login_successful"))
