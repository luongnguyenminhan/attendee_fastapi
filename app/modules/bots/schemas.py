from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel

from app.modules.bots.models import BotStates, MeetingTypes, RecordingFormats, RecordingViews

class BotBase(BaseModel):
    name: str = "My bot"
    meeting_url: str
    meeting_uuid: Optional[str] = None
    state: BotStates = BotStates.READY
    settings: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = None
    first_heartbeat_timestamp: Optional[int] = None
    last_heartbeat_timestamp: Optional[int] = None
    join_at: Optional[datetime] = None

class BotCreate(BotBase):
    project_id: int

class BotUpdate(BotBase):
    name: Optional[str] = None
    meeting_url: Optional[str] = None
    meeting_uuid: Optional[str] = None
    state: Optional[BotStates] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    first_heartbeat_timestamp: Optional[int] = None
    last_heartbeat_timestamp: Optional[int] = None
    join_at: Optional[datetime] = None

class BotRead(BotBase):
    id: int
    object_id: str
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


