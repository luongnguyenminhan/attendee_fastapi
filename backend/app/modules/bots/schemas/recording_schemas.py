from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.core.base_enums import (
    RecordingStates,
    RecordingTranscriptionStates,
    RecordingTypes,
    TranscriptionProviders,
    TranscriptionTypes,
)


class RecordingResponse(BaseModel):
    """Response schema for Recording"""

    id: str
    object_id: str
    bot_id: str
    recording_type: RecordingTypes
    transcription_type: TranscriptionTypes
    is_default_recording: bool
    state: RecordingStates
    transcription_state: RecordingTranscriptionStates
    transcription_provider: Optional[TranscriptionProviders] = None
    transcription_failure_data: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    first_buffer_timestamp_ms: Optional[int] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecordingListResponse(BaseModel):
    """Response schema for listing recordings"""

    recordings: List[RecordingResponse]
    total: int
    limit: int
    offset: int


class TranscriptResponse(BaseModel):
    """Response schema for transcript data"""

    id: str
    timestamp_ms: int
    duration_ms: int
    speaker: Optional[str] = None
    transcript: str
    confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None


class RecordingTranscriptsResponse(BaseModel):
    """Response schema for recording transcripts"""

    recording_id: str
    transcripts: List[TranscriptResponse]
    total_utterances: int
