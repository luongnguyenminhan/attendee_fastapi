from typing import Optional, List, Dict, Any
from sqlmodel import Session

from app.core.base_model import PaginationParams, PaginatedResponse
from app.exceptions.exception import (
    NotFoundException,
    ValidationException,
    ConflictException,
    UnauthorizedException,
)
from app.modules.bots.dal.bot_dal import BotDAL, BotEventDAL
from app.modules.bots.models.bot_model import (
    Bot,
    BotState,
    BotEvent,
    BotEventType,
    BotEventSubType,
)


class BotRepo:
    """Bot Repository - Business Logic Layer"""

    def __init__(self, session: Session):
        self.session = session
        self.bot_dal = BotDAL()
        self.event_dal = BotEventDAL()
        self.bot_dal.set_session(session)
        self.event_dal.set_session(session)

    async def create_bot(
        self,
        name: str,
        meeting_url: str,
        project_id: str,
        meeting_uuid: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        join_at: Optional[str] = None,
    ) -> Bot:
        """Create new bot with validation"""
        # Validate input
        if not name or len(name.strip()) < 2:
            raise ValidationException("bots.validation.name_too_short")

        if not meeting_url or not meeting_url.strip():
            raise ValidationException("bots.validation.meeting_url_required")

        if not project_id:
            raise ValidationException("bots.validation.project_required")

        # Validate meeting URL format
        if not self._is_valid_meeting_url(meeting_url.strip()):
            raise ValidationException("bots.validation.invalid_meeting_url")

        # Create bot
        bot = Bot(
            name=name.strip(),
            meeting_url=meeting_url.strip(),
            project_id=project_id,
            meeting_uuid=meeting_uuid,
            state=BotState.READY,
            settings=settings or {},
            join_at=join_at,
        )

        return await self.bot_dal.create(bot)

    async def get_bot_by_id(self, bot_id: str) -> Bot:
        """Get bot by ID with validation"""
        bot = await self.bot_dal.get_by_id(bot_id)
        if not bot:
            raise NotFoundException("bots.errors.not_found")
        return bot

    async def get_bot_by_object_id(self, object_id: str) -> Bot:
        """Get bot by object_id"""
        bot = await self.bot_dal.get_by_object_id(object_id)
        if not bot:
            raise NotFoundException("bots.errors.not_found")
        return bot

    async def update_bot(
        self,
        bot_id: str,
        name: Optional[str] = None,
        meeting_url: Optional[str] = None,
        meeting_uuid: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        join_at: Optional[str] = None,
    ) -> Bot:
        """Update bot with validation"""
        bot = await self.get_bot_by_id(bot_id)

        # Validate new name if provided
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ValidationException("bots.validation.name_too_short")
            bot.name = name.strip()

        # Validate new meeting URL if provided
        if meeting_url is not None:
            if not meeting_url or not meeting_url.strip():
                raise ValidationException("bots.validation.meeting_url_required")
            if not self._is_valid_meeting_url(meeting_url.strip()):
                raise ValidationException("bots.validation.invalid_meeting_url")
            bot.meeting_url = meeting_url.strip()

        if meeting_uuid is not None:
            bot.meeting_uuid = meeting_uuid

        if settings is not None:
            bot.settings = settings

        if join_at is not None:
            bot.join_at = join_at

        return await self.bot_dal.update(bot)

    async def delete_bot(self, bot_id: str) -> bool:
        """Soft delete bot"""
        bot = await self.get_bot_by_id(bot_id)
        return await self.bot_dal.delete(bot)

    async def get_bots_by_project(
        self,
        project_id: str,
        pagination: PaginationParams,
        state: Optional[BotState] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[Bot]:
        """Get paginated bots by project with filters"""

        if state and search:
            # Complex filtering
            bots = await self.bot_dal.get_by_state(state, project_id)
            if search:
                bots = [bot for bot in bots if search.lower() in bot.name.lower()]
            total = len(bots)
            start = pagination.offset
            end = start + pagination.limit
            items = bots[start:end]
        elif state:
            bots = await self.bot_dal.get_by_state(state, project_id)
            total = len(bots)
            start = pagination.offset
            end = start + pagination.limit
            items = bots[start:end]
        elif search:
            items = await self.bot_dal.search_by_name(search, project_id)
            total = len(items)
            start = pagination.offset
            end = start + pagination.limit
            items = items[start:end]
        else:
            # Get all by project then paginate
            all_bots = await self.bot_dal.get_by_project_id(project_id)
            total = len(all_bots)
            start = pagination.offset
            end = start + pagination.limit
            items = all_bots[start:end]

        return PaginatedResponse[Bot](
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.limit,
            pages=(total + pagination.limit - 1) // pagination.limit,
        )

    # Bot state management
    async def join_meeting(self, bot_id: str, recording: bool = False) -> Bot:
        """Make bot join meeting"""
        bot = await self.get_bot_by_id(bot_id)

        if not bot.can_join_meeting():
            raise ValidationException("bots.validation.cannot_join_meeting")

        # Update state
        old_state = bot.state
        bot.start_joining()
        await self.bot_dal.update(bot)

        # Create event
        await self._create_bot_event(
            bot_id=bot_id,
            old_state=old_state,
            new_state=bot.state,
            event_type=BotEventType.JOIN_REQUESTED,
        )

        return bot

    async def bot_joined_meeting(self, bot_id: str, recording: bool = False) -> Bot:
        """Update bot state when it successfully joins meeting"""
        bot = await self.get_bot_by_id(bot_id)

        old_state = bot.state
        bot.join_meeting(recording)
        bot.update_heartbeat()
        await self.bot_dal.update(bot)

        # Create event
        await self._create_bot_event(
            bot_id=bot_id,
            old_state=old_state,
            new_state=bot.state,
            event_type=BotEventType.BOT_JOINED_MEETING,
        )

        return bot

    async def start_recording(self, bot_id: str) -> Bot:
        """Start bot recording"""
        bot = await self.get_bot_by_id(bot_id)

        if not bot.is_active():
            raise ValidationException("bots.validation.bot_not_active")

        old_state = bot.state
        bot.start_recording()
        await self.bot_dal.update(bot)

        # Create event
        await self._create_bot_event(
            bot_id=bot_id,
            old_state=old_state,
            new_state=bot.state,
            event_type=BotEventType.BOT_RECORDING_PERMISSION_GRANTED,
        )

        return bot

    async def leave_meeting(self, bot_id: str) -> Bot:
        """Make bot leave meeting"""
        bot = await self.get_bot_by_id(bot_id)

        if not bot.can_leave_meeting():
            raise ValidationException("bots.validation.cannot_leave_meeting")

        old_state = bot.state
        bot.leave_meeting()
        await self.bot_dal.update(bot)

        # Create event
        await self._create_bot_event(
            bot_id=bot_id,
            old_state=old_state,
            new_state=bot.state,
            event_type=BotEventType.LEAVE_REQUESTED,
            event_sub_type=BotEventSubType.LEAVE_REQUESTED_USER,
        )

        return bot

    async def update_heartbeat(self, bot_id: str) -> Bot:
        """Update bot heartbeat"""
        bot = await self.get_bot_by_id(bot_id)
        bot.update_heartbeat()
        return await self.bot_dal.update(bot)

    async def set_bot_error(
        self, bot_id: str, error_details: Optional[Dict[str, Any]] = None
    ) -> Bot:
        """Set bot to error state"""
        bot = await self.get_bot_by_id(bot_id)

        old_state = bot.state
        bot.set_error()
        await self.bot_dal.update(bot)

        # Create event
        await self._create_bot_event(
            bot_id=bot_id,
            old_state=old_state,
            new_state=bot.state,
            event_type=BotEventType.FATAL_ERROR,
            metadata=error_details or {},
        )

        return bot

    # Bot events
    async def get_bot_events(self, bot_id: str, limit: int = 100) -> List[BotEvent]:
        """Get events for a bot"""
        await self.get_bot_by_id(bot_id)  # Validate bot exists
        return await self.event_dal.get_by_bot_id(bot_id, limit)

    # Utility methods
    async def get_active_bots(self, project_id: Optional[str] = None) -> List[Bot]:
        """Get all active bots"""
        return await self.bot_dal.get_active_bots(project_id)

    async def get_recording_bots(self, project_id: Optional[str] = None) -> List[Bot]:
        """Get bots that are currently recording"""
        return await self.bot_dal.get_recording_bots(project_id)

    async def get_bot_stats(self, bot_id: str) -> Dict[str, Any]:
        """Get bot statistics"""
        bot = await self.get_bot_by_id(bot_id)
        event_count = await self.event_dal.count_events_by_bot(bot_id)
        latest_event = await self.event_dal.get_latest_event_for_bot(bot_id)

        return {
            "bot_id": bot_id,
            "bot_name": bot.name,
            "state": bot.state.value,
            "is_active": bot.is_active(),
            "is_recording": bot.is_recording(),
            "total_events": event_count,
            "latest_event": latest_event.event_type.value if latest_event else None,
            "created_at": bot.created_at,
            "last_heartbeat": bot.last_heartbeat_timestamp,
        }

    # Private methods
    def _is_valid_meeting_url(self, url: str) -> bool:
        """Validate meeting URL format"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    async def _create_bot_event(
        self,
        bot_id: str,
        old_state: BotState,
        new_state: BotState,
        event_type: BotEventType,
        event_sub_type: Optional[BotEventSubType] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BotEvent:
        """Create a bot event"""
        event = BotEvent(
            bot_id=bot_id,
            old_state=old_state,
            new_state=new_state,
            event_type=event_type,
            event_sub_type=event_sub_type,
            metadata_=metadata or {},
        )

        return await self.event_dal.create(event)
