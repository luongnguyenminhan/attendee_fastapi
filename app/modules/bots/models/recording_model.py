import random
import string
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.dialects.mysql import JSON
from sqlmodel import Field, Relationship

from app.core.base_enums import (
    RecordingStates,
    RecordingTranscriptionStates,
    RecordingTypes,
    TranscriptionProviders,
    TranscriptionTypes,
)
from app.core.base_model import BaseEntity


class Recording(BaseEntity, table=True):
    __tablename__ = "recordings"

    # Core fields
    bot_id: UUID = Field(foreign_key="bots.id", index=True)
    recording_type: RecordingTypes = Field(default=RecordingTypes.AUDIO_AND_VIDEO)
    transcription_type: TranscriptionTypes = Field(default=TranscriptionTypes.NON_REALTIME)
    is_default_recording: bool = Field(default=False)

    # States
    state: RecordingStates = Field(default=RecordingStates.NOT_STARTED, index=True)
    transcription_state: RecordingTranscriptionStates = Field(default=RecordingTranscriptionStates.NOT_STARTED, index=True)

    # Transcription provider
    transcription_provider: Optional[TranscriptionProviders] = Field(default=None)
    transcription_failure_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)

    # Timing
    started_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)
    first_buffer_timestamp_ms: Optional[int] = Field(default=None)

    # File storage
    file_path: Optional[str] = Field(default=None, max_length=1000)
    file_size: Optional[int] = Field(default=None)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "rec_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    bot: "Bot" = Relationship(back_populates="recordings")
    utterances: list["Utterance"] = Relationship(back_populates="recording")

    def is_terminal_state(self) -> bool:
        """Check if recording is in a terminal state"""
        return self.state in [RecordingStates.COMPLETE, RecordingStates.FAILED]

    def is_transcription_complete(self) -> bool:
        """Check if transcription is complete"""
        return self.transcription_state == RecordingTranscriptionStates.COMPLETE

    def is_transcription_failed(self) -> bool:
        """Check if transcription failed"""
        return self.transcription_state == RecordingTranscriptionStates.FAILED

    def can_start_transcription(self) -> bool:
        """Check if transcription can be started"""
        return self.transcription_state == RecordingTranscriptionStates.NOT_STARTED and self.transcription_type != TranscriptionTypes.NO_TRANSCRIPTION

    def start_recording(self) -> None:
        """Start the recording"""
        if self.state == RecordingStates.NOT_STARTED:
            self.state = RecordingStates.IN_PROGRESS
            self.started_at = self.get_current_time().isoformat()

    def complete_recording(self) -> None:
        """Complete the recording"""
        if self.state == RecordingStates.IN_PROGRESS:
            self.state = RecordingStates.COMPLETE
            self.completed_at = self.get_current_time().isoformat()

    def fail_recording(self, error_message: str = None) -> None:
        """Fail the recording"""
        self.state = RecordingStates.FAILED
        if error_message:
            self.transcription_failure_data = {"error": error_message}

    def start_transcription(self) -> None:
        """Start transcription processing"""
        if self.can_start_transcription():
            self.transcription_state = RecordingTranscriptionStates.IN_PROGRESS

    def complete_transcription(self) -> None:
        """Complete transcription processing"""
        if self.transcription_state == RecordingTranscriptionStates.IN_PROGRESS:
            self.transcription_state = RecordingTranscriptionStates.COMPLETE

    def fail_transcription(self, failure_data: Dict[str, Any] = None) -> None:
        """Fail transcription processing"""
        self.transcription_state = RecordingTranscriptionStates.FAILED
        if failure_data:
            self.transcription_failure_data = failure_data

    def get_file_url(self) -> Optional[str]:
        """Generate temporary signed URL for file access"""
        if not self.file_path:
            return None
        # This would integrate with S3 or other storage
        # For now, return placeholder
        return f"/api/v1/recordings/{self.object_id}/download"

    def get_duration_ms(self) -> Optional[int]:
        """Get recording duration in milliseconds"""
        if not self.started_at or not self.completed_at:
            return None

        from datetime import datetime

        try:
            start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            return int((end - start).total_seconds() * 1000)
        except:
            return None

    def __repr__(self):
        return f"<Recording {self.object_id}: {self.state.value}>"
