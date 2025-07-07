from typing import Optional, Dict, Any
from pydantic import Field, validator

from app.core.base_model import RequestSchema
from app.modules.bots.models.bot_model import BotState


class CreateBotRequest(RequestSchema):
    """Create bot request schema"""

    name: str = Field(..., min_length=2, max_length=255, description="Bot name")
    meeting_url: str = Field(..., description="Meeting URL")
    project_id: str = Field(..., description="Project ID")
    meeting_uuid: Optional[str] = Field(None, description="Meeting UUID")
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Bot settings"
    )
    join_at: Optional[str] = Field(None, description="Scheduled join time (ISO format)")

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @validator("meeting_url")
    def validate_meeting_url(cls, v):
        if not v or not v.strip():
            raise ValueError("Meeting URL cannot be empty")
        return v.strip()


class UpdateBotRequest(RequestSchema):
    """Update bot request schema"""

    name: Optional[str] = Field(
        None, min_length=2, max_length=255, description="Bot name"
    )
    meeting_url: Optional[str] = Field(None, description="Meeting URL")
    meeting_uuid: Optional[str] = Field(None, description="Meeting UUID")
    settings: Optional[Dict[str, Any]] = Field(None, description="Bot settings")
    join_at: Optional[str] = Field(None, description="Scheduled join time (ISO format)")

    @validator("name")
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

    @validator("meeting_url")
    def validate_meeting_url(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Meeting URL cannot be empty")
        return v.strip() if v else v


class GetBotsRequest(RequestSchema):
    """Get bots request schema"""

    project_id: str = Field(..., description="Project ID")
    state: Optional[BotState] = Field(None, description="Filter by state")
    search: Optional[str] = Field(None, min_length=1, description="Search by name")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class JoinMeetingRequest(RequestSchema):
    """Join meeting request schema"""

    recording: bool = Field(default=False, description="Start recording immediately")


class BotActionRequest(RequestSchema):
    """General bot action request schema"""

    bot_id: str = Field(..., description="Bot ID")


class SetBotErrorRequest(RequestSchema):
    """Set bot error request schema"""

    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")
