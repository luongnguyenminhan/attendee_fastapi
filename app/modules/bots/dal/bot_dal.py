from typing import List, Optional

from sqlmodel import func, select

from app.core.base_dal import BaseDAL
from app.modules.bots.models.bot_model import Bot, BotEvent, BotEventType, BotState


class BotDAL(BaseDAL[Bot]):
    """Bot Data Access Layer"""

    def __init__(self):
        super().__init__(Bot)

    async def get_by_object_id(self, object_id: str) -> Optional[Bot]:
        """Get bot by object_id"""
        query = select(self.model).where(self.model.object_id == object_id, ~self.model.is_deleted)
        return await self._get_first(query)

    async def get_by_project_id(self, project_id: str) -> List[Bot]:
        """Get bots by project ID"""
        query = select(self.model).where(self.model.project_id == project_id, ~self.model.is_deleted).order_by(self.model.created_at.desc())
        return await self._get_all(query)

    async def get_by_state(self, state: BotState, project_id: Optional[str] = None) -> List[Bot]:
        """Get bots by state"""
        query = select(self.model).where(self.model.state == state, ~self.model.is_deleted)

        if project_id:
            query = query.where(self.model.project_id == project_id)

        return await self._get_all(query.order_by(self.model.created_at.desc()))

    async def get_active_bots(self, project_id: Optional[str] = None) -> List[Bot]:
        """Get all active bots"""
        active_states = [
            BotState.JOINING,
            BotState.JOINED_NOT_RECORDING,
            BotState.JOINED_RECORDING,
            BotState.JOINED_RECORDING_PAUSED,
            BotState.WAITING_ROOM,
        ]

        query = select(self.model).where(self.model.state.in_(active_states), ~self.model.is_deleted)

        if project_id:
            query = query.where(self.model.project_id == project_id)

        return await self._get_all(query.order_by(self.model.created_at.desc()))

    async def get_recording_bots(self, project_id: Optional[str] = None) -> List[Bot]:
        """Get bots that are currently recording"""
        return await self.get_by_state(BotState.JOINED_RECORDING, project_id)

    async def search_by_name(self, name_pattern: str, project_id: Optional[str] = None) -> List[Bot]:
        """Search bots by name pattern"""
        query = select(self.model).where(self.model.name.ilike(f"%{name_pattern}%"), ~self.model.is_deleted)

        if project_id:
            query = query.where(self.model.project_id == project_id)

        return await self._get_all(query.order_by(self.model.name))

    async def get_by_meeting_url(self, meeting_url: str) -> List[Bot]:
        """Get bots by meeting URL"""
        query = select(self.model).where(self.model.meeting_url == meeting_url, ~self.model.is_deleted).order_by(self.model.created_at.desc())
        return await self._get_all(query)

    async def count_by_project(self, project_id: str) -> int:
        """Count bots by project"""
        query = select(func.count(self.model.id)).where(self.model.project_id == project_id, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def get_bots_without_heartbeat(self, minutes: int = 5) -> List[Bot]:
        """Get active bots without recent heartbeat"""
        import time

        cutoff_time = int(time.time()) - (minutes * 60)

        query = select(self.model).where(
            self.model.state.in_(
                [
                    BotState.JOINING,
                    BotState.JOINED_NOT_RECORDING,
                    BotState.JOINED_RECORDING,
                    BotState.JOINED_RECORDING_PAUSED,
                ]
            ),
            self.model.last_heartbeat_timestamp < cutoff_time,
            ~self.model.is_deleted,
        )
        return await self._get_all(query)

    async def get_all_bots(self, skip: int = 0, limit: int = 20) -> List[Bot]:
        """Get all bots with pagination for admin"""
        query = select(self.model).where(~self.model.is_deleted).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        return await self._get_all(query)

    async def count_all_bots(self) -> int:
        """Count all bots"""
        query = select(func.count(self.model.id)).where(~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0

    async def count_by_state_all(self, state: BotState) -> int:
        """Count bots by state across all projects"""
        query = select(func.count(self.model.id)).where(self.model.state == state, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0


class BotEventDAL(BaseDAL[BotEvent]):
    """Bot Event Data Access Layer"""

    def __init__(self):
        super().__init__(BotEvent)

    async def get_by_bot_id(self, bot_id: str, limit: int = 100) -> List[BotEvent]:
        """Get events by bot ID"""
        query = select(self.model).where(self.model.bot_id == bot_id, ~self.model.is_deleted).order_by(self.model.created_at.desc()).limit(limit)
        return await self._get_all(query)

    async def get_by_event_type(self, event_type: BotEventType, bot_id: Optional[str] = None) -> List[BotEvent]:
        """Get events by type"""
        query = select(self.model).where(self.model.event_type == event_type, ~self.model.is_deleted)

        if bot_id:
            query = query.where(self.model.bot_id == bot_id)

        return await self._get_all(query.order_by(self.model.created_at.desc()))

    async def get_error_events(self, bot_id: Optional[str] = None) -> List[BotEvent]:
        """Get error events"""
        error_types = [BotEventType.FATAL_ERROR, BotEventType.COULD_NOT_JOIN]

        query = select(self.model).where(self.model.event_type.in_(error_types), ~self.model.is_deleted)

        if bot_id:
            query = query.where(self.model.bot_id == bot_id)

        return await self._get_all(query.order_by(self.model.created_at.desc()))

    async def get_latest_event_for_bot(self, bot_id: str) -> Optional[BotEvent]:
        """Get latest event for a bot"""
        query = select(self.model).where(self.model.bot_id == bot_id, ~self.model.is_deleted).order_by(self.model.created_at.desc()).limit(1)
        return await self._get_first(query)

    async def count_events_by_bot(self, bot_id: str) -> int:
        """Count events for a bot"""
        query = select(func.count(self.model.id)).where(self.model.bot_id == bot_id, ~self.model.is_deleted)
        result = await self._execute_query(query)
        return result.scalar() or 0
