from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
import re

from app.modules.users.dal.user_dal import UserDAL
from app.modules.users.models.user_model import User, UserStatus, UserRole
from app.exceptions.exception import (
    NotFoundException,
    ValidationException,
    ConflictException,
    BadRequestException,
)
from app.middlewares.translation_manager import _
from app.utils.security import get_password_hash, verify_password


class UserRepo:
    """Repository layer for User business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.user_dal = UserDAL(db)

    def _validate_email(self, email: str) -> None:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValidationException(_("invalid_email_format"))

    def _validate_password(self, password: str) -> None:
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationException(_("password_too_weak"))

        # Check for at least one uppercase, lowercase, digit and special character
        if not re.search(r"[A-Z]", password):
            raise ValidationException(_("password_needs_uppercase"))
        if not re.search(r"[a-z]", password):
            raise ValidationException(_("password_needs_lowercase"))
        if not re.search(r"\d", password):
            raise ValidationException(_("password_needs_digit"))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationException(_("password_needs_special_char"))

    def _validate_username(self, username: str) -> None:
        """Validate username format"""
        if len(username) < 3 or len(username) > 50:
            raise ValidationException(_("username_length_invalid"))

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise ValidationException(_("username_format_invalid"))

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID with validation"""
        user = await self.user_dal.get_by_id(user_id)
        if not user:
            raise NotFoundException(_("user_not_found"))
        return user

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email with validation"""
        self._validate_email(email)
        user = await self.user_dal.get_by_email(email)
        if not user:
            raise NotFoundException(_("user_not_found"))
        return user

    async def get_user_by_username(self, username: str) -> User:
        """Get user by username with validation"""
        user = await self.user_dal.get_by_username(username)
        if not user:
            raise NotFoundException(_("user_not_found"))
        return user

    async def authenticate_user(self, identifier: str, password: str) -> User:
        """Authenticate user with email/username and password"""
        user = await self.user_dal.get_by_email_or_username(identifier)
        if not user:
            raise NotFoundException(_("invalid_credentials"))

        if not verify_password(password, user.hashed_password):
            raise ValidationException(_("invalid_credentials"))

        if user.status != UserStatus.ACTIVE:
            raise ValidationException(_("user_account_inactive"))

        return user

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create new user with validation"""
        # Extract and validate data
        email = user_data.get("email")
        username = user_data.get("username")
        password = user_data.get("password")

        if not email or not username or not password:
            raise ValidationException(_("required_fields_missing"))

        # Validate input
        self._validate_email(email)
        self._validate_username(username)
        self._validate_password(password)

        # Check for existing users
        existing_user = await self.user_dal.get_by_email(email)
        if existing_user:
            raise ConflictException(_("email_already_exists"))

        existing_user = await self.user_dal.get_by_username(username)
        if existing_user:
            raise ConflictException(_("username_already_exists"))

        # Hash password and create user
        user_data["hashed_password"] = get_password_hash(password)
        del user_data["password"]  # Remove plain password

        # Set defaults
        user_data.setdefault("status", UserStatus.ACTIVE)
        user_data.setdefault("role", UserRole.USER)
        user_data.setdefault("is_email_verified", False)
        user_data.setdefault("is_superuser", False)

        return await self.user_dal.create(user_data)

    async def update_user(self, user_id: UUID, update_data: Dict[str, Any]) -> User:
        """Update user with validation"""
        user = await self.get_user_by_id(user_id)

        # Validate email if provided
        if "email" in update_data:
            self._validate_email(update_data["email"])
            # Check if email is already taken by another user
            existing_user = await self.user_dal.get_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ConflictException(_("email_already_exists"))

        # Validate username if provided
        if "username" in update_data:
            self._validate_username(update_data["username"])
            # Check if username is already taken by another user
            existing_user = await self.user_dal.get_by_username(update_data["username"])
            if existing_user and existing_user.id != user_id:
                raise ConflictException(_("username_already_exists"))

        # Handle password update
        if "password" in update_data:
            self._validate_password(update_data["password"])
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        return await self.user_dal.update(user_id, update_data)

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> User:
        """Change user password with current password verification"""
        user = await self.get_user_by_id(user_id)

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValidationException(_("current_password_incorrect"))

        # Validate new password
        self._validate_password(new_password)

        # Update password
        hashed_password = get_password_hash(new_password)
        return await self.user_dal.update_password(user_id, hashed_password)

    async def activate_user(self, user_id: UUID) -> User:
        """Activate user account"""
        return await self.user_dal.update_status(user_id, UserStatus.ACTIVE)

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate user account"""
        return await self.user_dal.update_status(user_id, UserStatus.INACTIVE)

    async def suspend_user(self, user_id: UUID) -> User:
        """Suspend user account"""
        return await self.user_dal.update_status(user_id, UserStatus.SUSPENDED)

    async def verify_user_email(self, user_id: UUID) -> User:
        """Mark user email as verified"""
        return await self.user_dal.verify_email(user_id)

    async def delete_user(self, user_id: UUID) -> bool:
        """Soft delete user"""
        user = await self.get_user_by_id(user_id)
        return await self.user_dal.delete(user_id, soft_delete=True)

    async def get_users_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get users by organization"""
        return await self.user_dal.get_by_organization_id(organization_id, skip, limit)

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        return await self.user_dal.get_active_users(skip, limit)

    async def search_users(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Search users by various fields"""
        if len(query.strip()) < 2:
            raise ValidationException(_("search_query_too_short"))

        return await self.user_dal.search_users(query.strip(), skip, limit)

    async def check_user_permissions(
        self, user_id: UUID, required_role: UserRole = None
    ) -> bool:
        """Check if user has required permissions"""
        user = await self.get_user_by_id(user_id)

        if not user.is_active:
            return False

        if user.is_superuser:
            return True

        if required_role and user.role != required_role:
            return False

        return True
