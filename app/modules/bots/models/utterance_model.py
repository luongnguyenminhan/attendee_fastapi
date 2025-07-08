import enum
import random
import string
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.core.base_model import BaseEntity


class UtteranceSource(str, enum.Enum):
    AUDIO_FROM_BOT = "audio_from_bot"
    CLOSED_CAPTION_FROM_PLATFORM = "closed_caption_from_platform"


class Utterance(BaseEntity, table=True):
    __tablename__ = "utterances"

    # Core fields
    recording_id: UUID = Field(foreign_key="recordings.id", index=True)
    participant_id: Optional[UUID] = Field(foreign_key="participants.id", index=True, default=None)

    # Audio data
    audio_blob: Optional[bytes] = Field(default=None)
    sample_rate: Optional[int] = Field(default=16000)

    # Timing
    timestamp_ms: int = Field(index=True)
    duration_ms: int = Field(default=0)

    # Transcription data
    transcription: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    transcription_attempt_count: int = Field(default=0)
    failure_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)

    # Source tracking
    source: UtteranceSource = Field(default=UtteranceSource.AUDIO_FROM_BOT)
    source_uuid: Optional[str] = Field(default=None, max_length=255)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "utt_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    recording: "Recording" = Relationship(back_populates="utterances")
    participant: Optional["Participant"] = Relationship(back_populates="utterances")

    def has_transcription(self) -> bool:
        """Check if utterance has transcription data"""
        return self.transcription is not None and bool(self.transcription.get("transcript"))

    def has_audio(self) -> bool:
        """Check if utterance has audio data"""
        return self.audio_blob is not None and len(self.audio_blob) > 0

    def has_failed(self) -> bool:
        """Check if transcription has failed"""
        return self.failure_data is not None

    def get_transcript_text(self) -> Optional[str]:
        """Get the transcript text"""
        if not self.transcription:
            return None
        return self.transcription.get("transcript")

    def get_speaker_name(self) -> Optional[str]:
        """Get speaker name from participant"""
        if self.participant:
            return self.participant.name
        return None

    def get_speaker_uuid(self) -> Optional[str]:
        """Get speaker UUID from participant"""
        if self.participant:
            return self.participant.object_id
        return None

    def get_confidence_score(self) -> Optional[float]:
        """Get transcription confidence score"""
        if not self.transcription:
            return None
        return self.transcription.get("confidence")

    def get_words(self) -> list:
        """Get word-level timestamps if available"""
        if not self.transcription:
            return []
        return self.transcription.get("words", [])

    def set_transcription(self, transcript: str, confidence: float = None, words: list = None) -> None:
        """Set transcription data"""
        self.transcription = {
            "transcript": transcript,
        }
        if confidence is not None:
            self.transcription["confidence"] = confidence
        if words:
            self.transcription["words"] = words

    def clear_audio_blob(self) -> None:
        """Clear audio blob to save space after transcription"""
        self.audio_blob = None

    def mark_transcription_failed(self, failure_reason: str, error_details: Dict[str, Any] = None) -> None:
        """Mark transcription as failed"""
        self.failure_data = {
            "reason": failure_reason,
            "attempt_count": self.transcription_attempt_count,
        }
        if error_details:
            self.failure_data.update(error_details)

    def can_retry_transcription(self) -> bool:
        """Check if transcription can be retried"""
        return not self.has_transcription() and self.transcription_attempt_count < 5 and self.has_audio()

    def increment_attempt_count(self) -> None:
        """Increment transcription attempt count"""
        self.transcription_attempt_count += 1

    def get_duration_seconds(self) -> float:
        """Get duration in seconds"""
        return self.duration_ms / 1000.0

    def get_timestamp_seconds(self) -> float:
        """Get timestamp in seconds"""
        return self.timestamp_ms / 1000.0

    def __repr__(self):
        speaker = self.get_speaker_name() or "Unknown"
        transcript = self.get_transcript_text()
        if transcript and len(transcript) > 50:
            transcript = transcript[:47] + "..."
        return f"<Utterance {self.object_id}: {speaker} - '{transcript}'>"
