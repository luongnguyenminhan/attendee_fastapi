from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.organizations.models import Organization

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, default_factory=lambda: str(uuid4())) # Default to UUID for username as in Django
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    organization: Optional[Organization] = Relationship(back_populates="users")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_staff: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    organization_id: Optional[int] = None


