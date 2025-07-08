import random
import string
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.core.base_enums import ParticipantEventTypes
from app.core.base_model import BaseEntity


class Participant(BaseEntity, table=True):
    __tablename__ = "participants"

    # Core fields
    bot_id: UUID = Field(foreign_key="bots.id", index=True)
    name: str = Field(max_length=255)

    # Meeting platform identifiers
    user_uuid: Optional[str] = Field(default=None, max_length=255, index=True)
    platform_user_id: Optional[str] = Field(default=None, max_length=255)

    # Participant status
    is_host: bool = Field(default=False)
    is_the_bot: bool = Field(default=False)
    is_active: bool = Field(default=True)

    # Metadata
    additional_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "par_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot: "Bot" = Relationship(back_populates="participants")
    utterances: List["Utterance"] = Relationship(back_populates="participant")
    chat_messages: List["ChatMessage"] = Relationship(back_populates="participant")
    participant_events: List["ParticipantEvent"] = Relationship(back_populates="participant")

    def join_meeting(self) -> None:
        """Mark participant as joined"""
        self.is_active = True

    def leave_meeting(self) -> None:
        """Mark participant as left"""
        self.is_active = False

    def get_display_name(self) -> str:
        """Get formatted display name"""
        status_indicators = []
        if self.is_host:
            status_indicators.append("Host")
        if self.is_the_bot:
            status_indicators.append("Bot")

        if status_indicators:
            return f"{self.name} ({', '.join(status_indicators)})"
        return self.name

    def get_join_events(self) -> List["ParticipantEvent"]:
        """Get all join events for this participant"""
        return [event for event in self.participant_events if event.event_type == ParticipantEventTypes.JOIN]

    def get_leave_events(self) -> List["ParticipantEvent"]:
        """Get all leave events for this participant"""
        return [event for event in self.participant_events if event.event_type == ParticipantEventTypes.LEAVE]

    def get_latest_join_event(self) -> Optional["ParticipantEvent"]:
        """Get the most recent join event"""
        join_events = self.get_join_events()
        if not join_events:
            return None
        return max(join_events, key=lambda e: e.timestamp_ms)

    def get_latest_leave_event(self) -> Optional["ParticipantEvent"]:
        """Get the most recent leave event"""
        leave_events = self.get_leave_events()
        if not leave_events:
            return None
        return max(leave_events, key=lambda e: e.timestamp_ms)

    def get_total_utterances(self) -> int:
        """Get total number of utterances"""
        return len(self.utterances)

    def get_total_speaking_time_ms(self) -> int:
        """Get total speaking time in milliseconds"""
        return sum(utterance.duration_ms for utterance in self.utterances)

    def get_total_speaking_time_seconds(self) -> float:
        """Get total speaking time in seconds"""
        return self.get_total_speaking_time_ms() / 1000.0

    def has_spoken(self) -> bool:
        """Check if participant has any utterances"""
        return len(self.utterances) > 0

    def __repr__(self):
        return f"<Participant {self.object_id}: {self.name}>"


class ParticipantEvent(BaseEntity, table=True):
    __tablename__ = "participant_events"

    # Core fields
    participant_id: UUID = Field(foreign_key="participants.id", index=True)
    event_type: ParticipantEventTypes = Field(index=True)
    timestamp_ms: int = Field(index=True)

    # Additional data
    event_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "pev_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    participant: "Participant" = Relationship(back_populates="participant_events")

    def get_timestamp_seconds(self) -> float:
        """Get timestamp in seconds"""
        return self.timestamp_ms / 1000.0

    def is_join_event(self) -> bool:
        """Check if this is a join event"""
        return self.event_type == ParticipantEventTypes.JOIN

    def is_leave_event(self) -> bool:
        """Check if this is a leave event"""
        return self.event_type == ParticipantEventTypes.LEAVE

    def get_event_description(self) -> str:
        """Get human-readable event description"""
        if self.is_join_event():
            return f"{self.participant.name} joined the meeting"
        elif self.is_leave_event():
            return f"{self.participant.name} left the meeting"
        return f"{self.participant.name} - {self.event_type.value}"

    def __repr__(self):
        return f"<ParticipantEvent {self.object_id}: {self.participant.name} - {self.event_type.value}>"
