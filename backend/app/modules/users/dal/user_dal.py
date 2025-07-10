from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select

from app.core.base_dal import BaseDAL
from app.modules.users.models.user_model import User, UserRole, UserStatus


class UserDAL(BaseDAL[User]):
    """Data Access Layer for User entity"""

    def __init__(self):
        super().__init__(None, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.db.execute(select(self.model).filter(and_(self.model.email == email, self.model.is_deleted == False)))
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            result = await self.db.execute(select(self.model).filter(and_(self.model.username == username, self.model.is_deleted == False)))
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        try:
            result = await self.db.execute(
                select(self.model).filter(
                    and_(
                        or_(
                            self.model.email == identifier,
                            self.model.username == identifier,
                        ),
                        self.model.is_deleted == False,
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_organization_id(self, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by organization ID"""
        try:
            result = await self.db.execute(
                select(self.model)
                .filter(
                    and_(
                        self.model.organization_id == organization_id,
                        self.model.is_deleted == False,
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        try:
            result = await self.db.execute(
                select(self.model)
                .filter(
                    and_(
                        self.model.status == UserStatus.ACTIVE,
                        self.model.is_deleted == False,
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        try:
            result = await self.db.execute(select(self.model).filter(and_(self.model.role == role, self.model.is_deleted == False)).offset(skip).limit(limit))
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_status(self, user_id: UUID, status: UserStatus) -> Optional[User]:
        """Update user status"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.status = status
                await self.db.flush()
                await self.db.refresh(user)
                return user
            return None
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_password(self, user_id: UUID, hashed_password: str) -> Optional[User]:
        """Update user password"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.hashed_password = hashed_password
                await self.db.flush()
                await self.db.refresh(user)
                return user
            return None
        except Exception as e:
            await self.db.rollback()
            raise e

    async def verify_email(self, user_id: UUID) -> Optional[User]:
        """Mark user email as verified"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.is_email_verified = True
                await self.db.flush()
                await self.db.refresh(user)
                return user
            return None
        except Exception as e:
            await self.db.rollback()
            raise e

    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by email, username, first_name, or last_name"""
        try:
            search_filter = or_(
                self.model.email.ilike(f"%{query}%"),
                self.model.username.ilike(f"%{query}%"),
                self.model.first_name.ilike(f"%{query}%"),
                self.model.last_name.ilike(f"%{query}%"),
            )

            result = await self.db.execute(select(self.model).filter(and_(search_filter, self.model.is_deleted == False)).offset(skip).limit(limit))
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users (non-deleted) with pagination"""
        try:
            result = await self.db.execute(select(self.model).filter(self.model.is_deleted == False).offset(skip).limit(limit))
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def count_total(self) -> int:
        """Count total non-deleted users"""
        try:
            result = await self.db.execute(select(func.count(self.model.id)).filter(self.model.is_deleted == False))
            return result.scalar() or 0
        except Exception as e:
            await self.db.rollback()
            raise e

    async def count_by_status(self, status: UserStatus) -> int:
        """Count users by status"""
        try:
            result = await self.db.execute(select(func.count(self.model.id)).filter(and_(self.model.status == status, self.model.is_deleted == False)))
            return result.scalar() or 0
        except Exception as e:
            await self.db.rollback()
            raise e
