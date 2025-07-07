from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4


# Base Entity for database models
class BaseEntity(SQLModel):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    create_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    update_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_deleted: bool = Field(default=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def dict(self) -> Dict[str, Any]:
        """Pydantic compatible dict method"""
        return self.to_dict()

    def items(self):
        """Dictionary-like items method"""
        return self.to_dict().items()


# Request Schema Base Classes
class RequestSchema(BaseModel):
    """Base class for request schemas"""

    model_config = ConfigDict(extra="forbid")


class FilterSchema(BaseModel):
    """Schema for dynamic filtering"""

    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, contains, icontains
    value: Any


class FilterableRequestSchema(RequestSchema):
    """Base class for filterable request schemas with pagination"""

    page: Optional[int] = Field(default=1, ge=1)
    page_size: Optional[int] = Field(default=10, ge=1, le=100)
    filters: Optional[List[FilterSchema]] = Field(default_factory=list)


# Response Schema Base Classes
class ResponseSchema(BaseModel):
    """Base class for response schemas"""

    model_config = ConfigDict(from_attributes=True)


class PagingInfo(BaseModel):
    """Pagination information"""

    total: int
    total_pages: int
    page: int
    page_size: int


class PaginationParams(BaseModel):
    """Pagination parameters for backward compatibility"""

    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    items: List[T]
    paging: PagingInfo


class APIResponse(BaseModel, Generic[T]):
    """Standard API response format"""

    error_code: int = 0
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(
        cls, data: Optional[T] = None, message: str = "success"
    ) -> "APIResponse[T]":
        """Create success response"""
        return cls(error_code=0, message=message, data=data)

    @classmethod
    def error(
        cls, error_code: int, message: str, data: Optional[T] = None
    ) -> "APIResponse[T]":
        """Create error response"""
        return cls(error_code=error_code, message=message, data=data)
