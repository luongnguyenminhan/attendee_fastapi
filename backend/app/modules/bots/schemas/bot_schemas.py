from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.core.base_enums import BotStates


class BotCreateRequest(BaseModel):
    """Request schema for creating bot"""

    name: str
    meeting_url: HttpUrl
    project_id: str
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BotUpdateRequest(BaseModel):
    """Request schema for updating bot"""

    name: Optional[str] = None
    meeting_url: Optional[HttpUrl] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BotResponse(BaseModel):
    """Response schema for Bot"""

    id: str
    object_id: str
    name: str
    meeting_url: str
    state: BotStates
    project_id: str
    settings: Dict[str, Any]
    metadata: Dict[str, Any]
    first_heartbeat_timestamp: Optional[int] = None
    last_heartbeat_timestamp: Optional[int] = None
    join_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BotListResponse(BaseModel):
    """Response schema for listing bots"""

    bots: List[BotResponse]
    total: int
    limit: int
    offset: int
