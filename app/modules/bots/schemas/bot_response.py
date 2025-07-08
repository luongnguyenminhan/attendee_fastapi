from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.base_model import APIResponse, PaginatedResponse, ResponseSchema
from app.modules.bots.models.bot_model import BotEventSubType, BotEventType, BotState


class BotResponse(ResponseSchema):
    """Bot response schema"""

    id: str
    name: str
    meeting_url: str
    meeting_uuid: Optional[str]
    state: BotState
    project_id: str
    object_id: str
    settings: Dict[str, Any]
    metadata_: Optional[Dict[str, Any]]
    first_heartbeat_timestamp: Optional[int]
    last_heartbeat_timestamp: Optional[int]
    join_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    display_name: str
    is_active: bool
    is_recording: bool
    can_join_meeting: bool
    can_leave_meeting: bool
    meeting_domain: Optional[str]

    @classmethod
    def from_entity(cls, bot) -> "BotResponse":
        """Convert Bot entity to response schema"""
        return cls(
            id=str(bot.id),
            name=bot.name,
            meeting_url=bot.meeting_url,
            meeting_uuid=bot.meeting_uuid,
            state=bot.state,
            project_id=bot.project_id,
            object_id=bot.object_id,
            settings=bot.settings,
            metadata_=bot.metadata_,
            first_heartbeat_timestamp=bot.first_heartbeat_timestamp,
            last_heartbeat_timestamp=bot.last_heartbeat_timestamp,
            join_at=bot.join_at,
            created_at=bot.created_at,
            updated_at=bot.updated_at,
            display_name=bot.get_display_name(),
            is_active=bot.is_active(),
            is_recording=bot.is_recording(),
            can_join_meeting=bot.can_join_meeting(),
            can_leave_meeting=bot.can_leave_meeting(),
            meeting_domain=bot.get_meeting_domain(),
        )


class BotListResponse(ResponseSchema):
    """Bot list item response schema"""

    id: str
    name: str
    meeting_url: str
    state: BotState
    project_id: str
    object_id: str
    is_active: bool
    is_recording: bool
    created_at: datetime
    last_heartbeat_timestamp: Optional[int]

    @classmethod
    def from_entity(cls, bot) -> "BotListResponse":
        """Convert Bot entity to list response schema"""
        return cls(
            id=str(bot.id),
            name=bot.name,
            meeting_url=bot.meeting_url,
            state=bot.state,
            project_id=bot.project_id,
            object_id=bot.object_id,
            is_active=bot.is_active(),
            is_recording=bot.is_recording(),
            created_at=bot.created_at,
            last_heartbeat_timestamp=bot.last_heartbeat_timestamp,
        )


class BotEventResponse(ResponseSchema):
    """Bot event response schema"""

    id: str
    old_state: BotState
    new_state: BotState
    event_type: BotEventType
    event_sub_type: Optional[BotEventSubType]
    metadata_: Dict[str, Any]
    requested_bot_action_taken_at: Optional[str]
    bot_id: str
    object_id: str
    created_at: datetime

    # Computed fields
    is_error_event: bool
    is_state_change: bool
    event_description: str

    @classmethod
    def from_entity(cls, event) -> "BotEventResponse":
        """Convert BotEvent entity to response schema"""
        return cls(
            id=str(event.id),
            old_state=event.old_state,
            new_state=event.new_state,
            event_type=event.event_type,
            event_sub_type=event.event_sub_type,
            metadata_=event.metadata_,
            requested_bot_action_taken_at=event.requested_bot_action_taken_at,
            bot_id=event.bot_id,
            object_id=event.object_id,
            created_at=event.created_at,
            is_error_event=event.is_error_event(),
            is_state_change=event.is_state_change(),
            event_description=event.get_event_description(),
        )


class BotStatsResponse(ResponseSchema):
    """Bot statistics response schema"""

    bot_id: str
    bot_name: str
    state: str
    is_active: bool
    is_recording: bool
    total_events: int
    latest_event: Optional[str]
    created_at: datetime
    last_heartbeat: Optional[int]


class BotActionResponse(ResponseSchema):
    """Bot action response schema"""

    bot_id: str
    action: str
    old_state: Optional[str] = None
    new_state: str
    success: bool
    message: str

    @classmethod
    def success_action(cls, bot, action: str, old_state: Optional[BotState] = None) -> "BotActionResponse":
        """Create successful action response"""
        return cls(
            bot_id=str(bot.id),
            action=action,
            old_state=old_state.value if old_state else None,
            new_state=bot.state.value,
            success=True,
            message=f"Bot {action} successful",
        )


# API Response types
BotAPIResponse = APIResponse[BotResponse]
BotListAPIResponse = APIResponse[List[BotListResponse]]
BotPaginatedAPIResponse = APIResponse[PaginatedResponse[BotListResponse]]
BotStatsAPIResponse = APIResponse[BotStatsResponse]
BotActionAPIResponse = APIResponse[BotActionResponse]
BotEventListAPIResponse = APIResponse[List[BotEventResponse]]
