from contextlib import contextmanager
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.base_model import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseDAL(Generic[T]):
    """Base Data Access Layer with standard CRUD operations"""

    def __init__(self, db: Union[Session, AsyncSession] = None, model: Optional[Type[T]] = None):
        self.db = db
        self.model = model

    def set_session(self, session: Union[Session, AsyncSession]):
        """Set database session for DAL"""
        self.db = session

    # CRUD Operations
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id, self.model.is_deleted == False).first()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all entities with optional filters"""
        try:
            query = self.db.query(self.model).filter(self.model.is_deleted == False)

            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)

            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def create(self, entity_data: Dict[str, Any]) -> T:
        """Create new entity"""
        try:
            db_entity = self.model(**entity_data)
            self.db.add(db_entity)
            self.db.flush()
            self.db.refresh(db_entity)
            return db_entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def update(self, id: UUID, update_data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID"""
        try:
            db_entity = await self.get_by_id(id)
            if not db_entity:
                return None

            for field, value in update_data.items():
                if hasattr(db_entity, field):
                    setattr(db_entity, field, value)

            self.db.flush()
            self.db.refresh(db_entity)
            return db_entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def delete(self, id: UUID, soft_delete: bool = True) -> bool:
        """Delete entity (soft delete by default)"""
        try:
            db_entity = await self.get_by_id(id)
            if not db_entity:
                return False

            if soft_delete:
                db_entity.is_deleted = True
                self.db.flush()
            else:
                self.db.delete(db_entity)

            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        try:
            query = self.db.query(self.model).filter(self.model.is_deleted == False)

            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)

            return query.count()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # Transaction Management
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            yield self.db
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def begin_transaction(self):
        """Begin a new transaction"""
        self.db.begin()

    def commit(self):
        """Commit current transaction"""
        self.db.commit()

    def rollback(self):
        """Rollback current transaction"""
        self.db.rollback()

    # Helper methods for complex queries
    def get_query(self):
        """Get base query for the model"""
        return self.db.query(self.model).filter(self.model.is_deleted == False)

    async def _execute_query(self, query):
        """Execute query - supports both sync and async sessions"""
        if hasattr(self.db, "execute"):  # AsyncSession
            return await self.db.execute(query)
        else:  # Sync Session
            return self.db.execute(query)

    async def _get_first(self, query):
        """Get first result from query"""
        result = await self._execute_query(query)
        if hasattr(result, "scalar_one_or_none"):  # AsyncSession result
            return result.scalar_one_or_none()
        else:  # Sync Session result
            return result.first()

    async def _get_all(self, query):
        """Get all results from query"""
        result = await self._execute_query(query)
        if hasattr(result, "scalars"):  # AsyncSession result
            return result.scalars().all()
        else:  # Sync Session result
            return result.all()

    async def _begin_transaction(self):
        """Begin transaction"""
        if hasattr(self.db, "begin"):
            await self.db.begin()
        else:
            self.db.begin()

    async def _commit_transaction(self):
        """Commit transaction"""
        if hasattr(self.db, "commit"):
            await self.db.commit()
        else:
            self.db.commit()

    async def _rollback_transaction(self):
        """Rollback transaction"""
        if hasattr(self.db, "rollback"):
            await self.db.rollback()
        else:
            self.db.rollback()

    async def exists(self, **filters) -> bool:
        """Check if entity exists with given filters"""
        try:
            query = self.get_query()
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

            return query.first() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
