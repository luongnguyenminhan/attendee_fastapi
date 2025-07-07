from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
import random
import string

from app.modules.organizations.models import Organization

class ProjectBase(SQLModel):
    name: str = Field(index=True)
    organization_id: int = Field(foreign_key="organization.id")

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "proj_" + ''.join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    organization: Optional[Organization] = Relationship(back_populates="projects")
    bots: List["Bot"] = Relationship(back_populates="project")
    api_keys: List["ApiKey"] = Relationship(back_populates="project")
    credentials: List["Credential"] = Relationship(back_populates="project")
    media_blobs: List["MediaBlob"] = Relationship(back_populates="project")
    webhook_secrets: List["WebhookSecret"] = Relationship(back_populates="project")
    webhook_subscriptions: List["WebhookSubscription"] = Relationship(back_populates="project")

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int
    object_id: str
    created_at: datetime
    updated_at: datetime

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    organization_id: Optional[int] = None





class ApiKeyBase(SQLModel):
    name: str
    project_id: int = Field(foreign_key="project.id")

class ApiKey(ApiKeyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "key_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    key_hash: str = Field(max_length=64, unique=True)
    disabled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="api_keys")

class ApiKeyCreate(ApiKeyBase):
    plain_key: str # To receive the plain text key for hashing

class ApiKeyRead(ApiKeyBase):
    id: int
    object_id: str
    key_hash: str
    disabled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class ApiKeyUpdate(SQLModel):
    name: Optional[str] = None
    disabled_at: Optional[datetime] = None


