from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class OrganizationBase(SQLModel):
    name: str = Field(index=True)
    centicredits: int = Field(default=500)
    is_webhooks_enabled: bool = Field(default=True)

class Organization(OrganizationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    users: List["User"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")
    credit_transactions: List["CreditTransaction"] = Relationship(back_populates="organization")

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

class OrganizationUpdate(SQLModel):
    name: Optional[str] = None
    centicredits: Optional[int] = None
    is_webhooks_enabled: Optional[bool] = None

