import random
import string
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.dialects.mysql import JSON
from sqlmodel import Field, Relationship

from app.core.base_enums import ChatMessageToOptions
from app.core.base_model import BaseEntity


class ChatMessage(BaseEntity, table=True):
    __tablename__ = "chat_messages"

    # Core fields
    bot_id: UUID = Field(foreign_key="bots.id", index=True)
    participant_id: Optional[UUID] = Field(foreign_key="participants.id", index=True, default=None)

    # Message content
    text: str = Field(max_length=10000)
    to: ChatMessageToOptions = Field(default=ChatMessageToOptions.EVERYONE)

    # Timing
    timestamp: int = Field(index=True)  # Unix timestamp
    timestamp_ms: Optional[int] = Field(default=None, index=True)  # Milliseconds timestamp

    # Sender information
    sender_name: Optional[str] = Field(default=None, max_length=255)
    sender_uuid: Optional[str] = Field(default=None, max_length=255)
    sender_user_uuid: Optional[str] = Field(default=None, max_length=255)

    # Additional data
    additional_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "msg_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot: "Bot" = Relationship(back_populates="chat_messages")
    participant: Optional["Participant"] = Relationship(back_populates="chat_messages")

    def is_from_bot(self) -> bool:
        """Check if message is from the bot"""
        return (self.participant and self.participant.is_the_bot) or self.sender_name == "Bot"

    def is_to_bot_only(self) -> bool:
        """Check if message is directed to bot only"""
        return self.to == ChatMessageToOptions.ONLY_BOT

    def is_to_everyone(self) -> bool:
        """Check if message is to everyone"""
        return self.to == ChatMessageToOptions.EVERYONE

    def get_sender_display_name(self) -> str:
        """Get formatted sender name"""
        if self.participant:
            return self.participant.get_display_name()
        return self.sender_name or "Unknown"

    def get_timestamp_ms(self) -> int:
        """Get timestamp in milliseconds"""
        if self.timestamp_ms is not None:
            return self.timestamp_ms
        return self.timestamp * 1000

    def get_timestamp_seconds(self) -> float:
        """Get timestamp in seconds"""
        return self.get_timestamp_ms() / 1000.0

    def get_formatted_timestamp(self) -> str:
        """Get formatted timestamp string"""
        from datetime import datetime

        dt = datetime.fromtimestamp(self.get_timestamp_seconds())
        return dt.strftime("%H:%M:%S")

    def get_message_preview(self, max_length: int = 100) -> str:
        """Get truncated message preview"""
        if len(self.text) <= max_length:
            return self.text
        return self.text[: max_length - 3] + "..."

    def is_command(self) -> bool:
        """Check if message looks like a command (starts with /)"""
        return self.text.strip().startswith("/")

    def get_command(self) -> Optional[str]:
        """Extract command from message if it's a command"""
        if not self.is_command():
            return None
        return self.text.strip().split()[0][1:]  # Remove the "/" and get first word

    def contains_mention(self, name: str) -> bool:
        """Check if message contains a mention of the given name"""
        return name.lower() in self.text.lower()

    def __repr__(self):
        sender = self.get_sender_display_name()
        preview = self.get_message_preview(30)
        return f"<ChatMessage {self.object_id}: {sender} - '{preview}'>"


class BotChatMessageRequest(BaseEntity, table=True):
    __tablename__ = "bot_chat_message_requests"

    # Core fields
    bot_id: UUID = Field(foreign_key="bots.id", index=True)
    text: str = Field(max_length=10000)

    # Status tracking
    state: int = Field(default=1, index=True)  # 1=pending, 2=success, 3=failure
    failure_reason: Optional[str] = Field(default=None, max_length=1000)

    # Timing
    requested_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "bcr_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot: "Bot" = Relationship(back_populates="chat_message_requests")

    def is_pending(self) -> bool:
        """Check if request is pending"""
        return self.state == 1

    def is_completed(self) -> bool:
        """Check if request is completed successfully"""
        return self.state == 2

    def is_failed(self) -> bool:
        """Check if request failed"""
        return self.state == 3

    def mark_pending(self) -> None:
        """Mark request as pending"""
        self.state = 1
        self.requested_at = self.get_current_time().isoformat()

    def mark_completed(self) -> None:
        """Mark request as completed"""
        self.state = 2
        self.completed_at = self.get_current_time().isoformat()

    def mark_failed(self, reason: str) -> None:
        """Mark request as failed"""
        self.state = 3
        self.failure_reason = reason
        self.completed_at = self.get_current_time().isoformat()

    def get_status_display(self) -> str:
        """Get human-readable status"""
        if self.is_pending():
            return "Pending"
        elif self.is_completed():
            return "Completed"
        elif self.is_failed():
            return f"Failed: {self.failure_reason}"
        return "Unknown"

    def __repr__(self):
        status = self.get_status_display()
        preview = self.text[:30] + "..." if len(self.text) > 30 else self.text
        return f"<BotChatMessageRequest {self.object_id}: {status} - '{preview}'>"
