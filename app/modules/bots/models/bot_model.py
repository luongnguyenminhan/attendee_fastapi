from typing import Optional, List, Any, Dict, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
import random
import string
from uuid import UUID
import os
import math

from app.core.base_model import BaseEntity
from app.core.base_enums import BaseEnum, BotStates, RecordingTypes, MeetingTypes

if TYPE_CHECKING:
    from .webhook_model import WebhookSubscription, WebhookDeliveryAttempt
    from .chat_message_model import BotChatMessageRequest, ChatMessage
    from .participant_model import Participant
    from .recording_model import Recording
    from .credit_transaction_model import CreditTransaction
    from ...projects.models.project_model import Project


class MeetingType(BaseEnum):
    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"


class BotState(BaseEnum):
    READY = "ready"
    JOINING = "joining"
    JOINED_NOT_RECORDING = "joined_not_recording"
    JOINED_RECORDING = "joined_recording"
    LEAVING = "leaving"
    POST_PROCESSING = "post_processing"
    FATAL_ERROR = "fatal_error"
    WAITING_ROOM = "waiting_room"
    ENDED = "ended"
    DATA_DELETED = "data_deleted"
    SCHEDULED = "scheduled"
    STAGED = "staged"
    JOINED_RECORDING_PAUSED = "joined_recording_paused"


class BotEventType(BaseEnum):
    BOT_PUT_IN_WAITING_ROOM = "bot_put_in_waiting_room"
    BOT_JOINED_MEETING = "bot_joined_meeting"
    BOT_RECORDING_PERMISSION_GRANTED = "bot_recording_permission_granted"
    MEETING_ENDED = "meeting_ended"
    BOT_LEFT_MEETING = "bot_left_meeting"
    JOIN_REQUESTED = "join_requested"
    FATAL_ERROR = "fatal_error"
    LEAVE_REQUESTED = "leave_requested"
    COULD_NOT_JOIN = "could_not_join"
    POST_PROCESSING = "post_processing"
    DATA_DELETED = "data_deleted"
    STAGED = "staged"
    RECORDING_PAUSED = "recording_paused"
    RECORDING_RESUMED = "recording_resumed"


class BotEventSubType(BaseEnum):
    COULD_NOT_JOIN_MEETING_NOT_STARTED = "could_not_join_meeting_not_started"
    FATAL_ERROR_PROCESS_TERMINATED = "fatal_error_process_terminated"
    COULD_NOT_JOIN_ZOOM_AUTH_FAILED = "could_not_join_zoom_auth_failed"
    COULD_NOT_JOIN_ZOOM_STATUS_FAILED = "could_not_join_zoom_status_failed"
    FATAL_ERROR_RTMP_CONNECTION_FAILED = "fatal_error_rtmp_connection_failed"
    FATAL_ERROR_UI_ELEMENT_NOT_FOUND = "fatal_error_ui_element_not_found"
    LEAVE_REQUESTED_USER = "leave_requested_user"
    LEAVE_REQUESTED_AUTO_SILENCE = "leave_requested_auto_silence"
    FATAL_ERROR_HEARTBEAT_TIMEOUT = "fatal_error_heartbeat_timeout"
    FATAL_ERROR_OUT_OF_CREDITS = "fatal_error_out_of_credits"


class BotEvent(BaseEntity, table=True):
    __tablename__ = "botevent"

    # State transition
    old_state: BotState = Field(index=True)
    new_state: BotState = Field(index=True)

    # Event details
    event_type: BotEventType = Field(index=True)
    event_sub_type: Optional[BotEventSubType] = Field(default=None)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)

    # Timing
    requested_bot_action_taken_at: Optional[str] = Field(default=None)

    # Foreign key
    bot_id: UUID = Field(foreign_key="bots.id", index=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "bevt_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot: "Bot" = Relationship(back_populates="bot_events")
    screenshots: list["BotDebugScreenshot"] = Relationship(back_populates="bot_event")

    # Domain/business logic methods
    def is_error_event(self) -> bool:
        """Check if this is an error event"""
        error_types = [BotEventType.FATAL_ERROR, BotEventType.COULD_NOT_JOIN]
        return self.event_type in error_types

    def is_state_change(self) -> bool:
        """Check if this event represents a state change"""
        return self.old_state != self.new_state

    def get_event_description(self) -> str:
        """Get human-readable event description"""
        base_desc = (
            f"Bot transitioned from {self.old_state.value} to {self.new_state.value}"
        )
        if self.event_sub_type:
            base_desc += f" ({self.event_sub_type.value})"
        return base_desc

    def get_duration_since_request(self) -> Optional[int]:
        """Get duration since bot action was requested (in seconds)"""
        if not self.requested_bot_action_taken_at:
            return None
        try:
            from datetime import datetime

            requested_time = datetime.fromisoformat(self.requested_bot_action_taken_at)
            duration = (self.created_at - requested_time).total_seconds()
            return int(duration)
        except:
            return None


class Bot(BaseEntity, table=True):
    __tablename__ = "bots"

    # Core fields
    name: str = Field(default="My bot", max_length=255)
    meeting_url: str = Field(max_length=511, index=True)
    meeting_uuid: Optional[str] = Field(default=None, max_length=511)
    state: BotState = Field(default=BotState.READY, index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "bot_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Configuration and metadata
    settings: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    metadata_: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)

    # Timing and heartbeat
    first_heartbeat_timestamp: Optional[int] = Field(default=None)
    last_heartbeat_timestamp: Optional[int] = Field(default=None)
    join_at: Optional[str] = Field(default=None)

    # Relationships
    project: "Project" = Relationship(back_populates="bots")
    recordings: list["Recording"] = Relationship(back_populates="bot")
    participants: list["Participant"] = Relationship(back_populates="bot")
    chat_messages: list["ChatMessage"] = Relationship(back_populates="bot")
    chat_message_requests: list["BotChatMessageRequest"] = Relationship(
        back_populates="bot"
    )
    bot_events: list["BotEvent"] = Relationship(back_populates="bot")
    webhook_subscriptions: list["WebhookSubscription"] = Relationship(
        back_populates="bot"
    )
    webhook_delivery_attempts: list["WebhookDeliveryAttempt"] = Relationship(
        back_populates="bot"
    )
    credit_transactions: list["CreditTransaction"] = Relationship(back_populates="bot")

    # Domain/business logic methods
    def is_active(self) -> bool:
        """Check if bot is in an active state"""
        active_states = [
            BotState.JOINING,
            BotState.JOINED_NOT_RECORDING,
            BotState.JOINED_RECORDING,
            BotState.JOINED_RECORDING_PAUSED,
            BotState.WAITING_ROOM,
        ]
        return self.state in active_states and not self.is_deleted

    def is_recording(self) -> bool:
        """Check if bot is currently recording"""
        return self.state == BotState.JOINED_RECORDING

    def can_join_meeting(self) -> bool:
        """Check if bot can join a meeting"""
        return (
            self.state in [BotState.READY, BotState.SCHEDULED] and not self.is_deleted
        )

    def can_leave_meeting(self) -> bool:
        """Check if bot can leave a meeting"""
        return self.is_active()

    def start_joining(self) -> None:
        """Set bot state to joining"""
        self.state = BotState.JOINING

    def join_meeting(self, recording: bool = False) -> None:
        """Set bot state to joined"""
        if recording:
            self.state = BotState.JOINED_RECORDING
        else:
            self.state = BotState.JOINED_NOT_RECORDING

    def start_recording(self) -> None:
        """Start recording"""
        if self.state == BotState.JOINED_NOT_RECORDING:
            self.state = BotState.JOINED_RECORDING

    def pause_recording(self) -> None:
        """Pause recording"""
        if self.state == BotState.JOINED_RECORDING:
            self.state = BotState.JOINED_RECORDING_PAUSED

    def resume_recording(self) -> None:
        """Resume recording"""
        if self.state == BotState.JOINED_RECORDING_PAUSED:
            self.state = BotState.JOINED_RECORDING

    def leave_meeting(self) -> None:
        """Set bot state to leaving"""
        self.state = BotState.LEAVING

    def end_meeting(self) -> None:
        """Set bot state to ended"""
        self.state = BotState.ENDED

    def set_error(self) -> None:
        """Set bot state to fatal error"""
        self.state = BotState.FATAL_ERROR

    def update_heartbeat(self) -> None:
        """Update last heartbeat timestamp"""
        current_timestamp = int(self.get_current_time().timestamp())
        if self.first_heartbeat_timestamp is None:
            self.first_heartbeat_timestamp = current_timestamp
        self.last_heartbeat_timestamp = current_timestamp

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.state.value})"

    def get_meeting_domain(self) -> Optional[str]:
        """Extract domain from meeting URL"""
        if not self.meeting_url:
            return None
        try:
            from urllib.parse import urlparse

            parsed = urlparse(self.meeting_url)
            return parsed.netloc
        except:
            return None

    def recording_type(self):
        """Determine recording type from settings"""
        recording_settings = self.settings.get("recording_settings", {})
        if recording_settings.get("format") == "mp3":
            return RecordingTypes.AUDIO_ONLY
        return RecordingTypes.AUDIO_AND_VIDEO

    def meeting_type(self):
        """Determine meeting type from URL"""
        if "zoom.us" in self.meeting_url:
            return MeetingTypes.ZOOM
        elif "meet.google.com" in self.meeting_url:
            return MeetingTypes.GOOGLE_MEET
        elif "teams.microsoft.com" in self.meeting_url:
            return MeetingTypes.TEAMS
        return None

    def centicredits_consumed(self) -> int:
        """Calculate credits consumed based on bot runtime"""
        if (
            self.first_heartbeat_timestamp is None
            or self.last_heartbeat_timestamp is None
        ):
            return 0
        if self.last_heartbeat_timestamp < self.first_heartbeat_timestamp:
            return 0

        seconds_active = self.last_heartbeat_timestamp - self.first_heartbeat_timestamp
        # If first and last heartbeat are the same, assume 30 seconds
        if self.last_heartbeat_timestamp == self.first_heartbeat_timestamp:
            seconds_active = 30

        hours_active = seconds_active / 3600
        # Rate is 1 credit per hour
        centicredits_active = hours_active * 100
        return math.ceil(centicredits_active)

    def cpu_request(self):
        """Get CPU request based on meeting type and recording type"""
        meeting_type = self.meeting_type()
        recording_type = self.recording_type()

        meeting_type_env_var_substring = {
            MeetingTypes.GOOGLE_MEET: "GOOGLE_MEET",
            MeetingTypes.TEAMS: "TEAMS",
            MeetingTypes.ZOOM: "ZOOM",
        }.get(meeting_type, "UNKNOWN")

        recording_mode_env_var_substring = {
            RecordingTypes.AUDIO_AND_VIDEO: "AUDIO_AND_VIDEO",
            RecordingTypes.AUDIO_ONLY: "AUDIO_ONLY",
        }.get(recording_type, "UNKNOWN")

        env_var_name = f"{meeting_type_env_var_substring}_{recording_mode_env_var_substring}_BOT_CPU_REQUEST"

        default_cpu_request = os.getenv("BOT_CPU_REQUEST", "4") or "4"
        value_from_env_var = os.getenv(env_var_name, default_cpu_request)
        if not value_from_env_var:
            return default_cpu_request
        return value_from_env_var

    def k8s_pod_name(self):
        """Generate Kubernetes pod name"""
        return f"bot-{self.object_id.replace('_', '-')}"

    # Transcription settings helper methods
    def deepgram_model(self):
        return (
            self.settings.get("transcription_settings", {})
            .get("deepgram", {})
            .get("model", "nova-2")
        )

    def deepgram_language(self):
        return (
            self.settings.get("transcription_settings", {})
            .get("deepgram", {})
            .get("language", "multi")
        )

    def deepgram_detect_language(self):
        return (
            self.settings.get("transcription_settings", {})
            .get("deepgram", {})
            .get("detect_language", False)
        )

    def openai_transcription_model(self):
        return (
            self.settings.get("transcription_settings", {})
            .get("openai", {})
            .get("model", "whisper-1")
        )

    def openai_transcription_prompt(self):
        return (
            self.settings.get("transcription_settings", {})
            .get("openai", {})
            .get("prompt", None)
        )

    def __repr__(self):
        return f"<Bot {self.object_id}: {self.name}>"


class BotDebugScreenshot(BaseEntity, table=True):
    __tablename__ = "botdebugscreenshot"

    # Core fields
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    file_url: Optional[str] = Field(default=None, max_length=1000)

    # Foreign key
    bot_event_id: UUID = Field(foreign_key="botevent.id", index=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "shot_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot_event: "BotEvent" = Relationship(back_populates="screenshots")

    # Domain/business logic methods
    def has_file(self) -> bool:
        """Check if screenshot has a file URL"""
        return bool(self.file_url)

    def get_file_extension(self) -> Optional[str]:
        """Get file extension from URL"""
        if not self.file_url:
            return None
        try:
            import os

            return os.path.splitext(self.file_url)[1].lower()
        except:
            return None

    def is_image(self) -> bool:
        """Check if file is an image"""
        ext = self.get_file_extension()
        return ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"] if ext else False
