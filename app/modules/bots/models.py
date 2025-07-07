from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
import random
import string
from enum import Enum

from sqlalchemy.dialects.postgresql import JSONB

from app.modules.projects.models import Project
from app.modules.users.models import User
from app.modules.organizations.models import Organization

class MeetingTypes(str, Enum):
    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"

class BotStates(int, Enum):
    READY = 1
    JOINING = 2
    JOINED_NOT_RECORDING = 3
    JOINED_RECORDING = 4
    LEAVING = 5
    POST_PROCESSING = 6
    FATAL_ERROR = 7
    WAITING_ROOM = 8
    ENDED = 9
    DATA_DELETED = 10
    SCHEDULED = 11
    STAGED = 12
    JOINED_RECORDING_PAUSED = 13

class RecordingFormats(str, Enum):
    MP4 = "mp4"
    WEBM = "webm"
    MP3 = "mp3"

class RecordingViews(str, Enum):
    SPEAKER_VIEW = "speaker_view"
    GALLERY_VIEW = "gallery_view"


class BotEventTypes(int, Enum):
    BOT_PUT_IN_WAITING_ROOM = 1
    BOT_JOINED_MEETING = 2
    BOT_RECORDING_PERMISSION_GRANTED = 3
    MEETING_ENDED = 4
    BOT_LEFT_MEETING = 5
    JOIN_REQUESTED = 6
    FATAL_ERROR = 7
    LEAVE_REQUESTED = 8
    COULD_NOT_JOIN = 9
    POST_PROCESSING = 10
    DATA_DELETED = 11
    STAGED = 12
    RECORDING_PAUSED = 13
    RECORDING_RESUMED = 14

class BotEventSubTypes(int, Enum):
    COULD_NOT_JOIN_MEETING_NOT_STARTED_WAITING_FOR_HOST = 1
    FATAL_ERROR_PROCESS_TERMINATED = 2
    COULD_NOT_JOIN_MEETING_ZOOM_AUTHORIZATION_FAILED = 3
    COULD_NOT_JOIN_MEETING_ZOOM_MEETING_STATUS_FAILED = 4
    COULD_NOT_JOIN_MEETING_UNPUBLISHED_ZOOM_APP = 5
    FATAL_ERROR_RTMP_CONNECTION_FAILED = 6
    COULD_NOT_JOIN_MEETING_ZOOM_SDK_INTERNAL_ERROR = 7
    FATAL_ERROR_UI_ELEMENT_NOT_FOUND = 8
    COULD_NOT_JOIN_MEETING_REQUEST_TO_JOIN_DENIED = 9
    LEAVE_REQUESTED_USER_REQUESTED = 10
    LEAVE_REQUESTED_AUTO_LEAVE_SILENCE = 11
    LEAVE_REQUESTED_AUTO_LEAVE_ONLY_PARTICIPANT_IN_MEETING = 12
    FATAL_ERROR_HEARTBEAT_TIMEOUT = 13
    COULD_NOT_JOIN_MEETING_MEETING_NOT_FOUND = 14
    FATAL_ERROR_BOT_NOT_LAUNCHED = 15
    COULD_NOT_JOIN_MEETING_WAITING_ROOM_TIMEOUT_EXCEEDED = 16
    LEAVE_REQUESTED_AUTO_LEAVE_MAX_UPTIME_EXCEEDED = 17
    COULD_NOT_JOIN_MEETING_LOGIN_REQUIRED = 18
    COULD_NOT_JOIN_MEETING_BOT_LOGIN_ATTEMPT_FAILED = 19
    FATAL_ERROR_OUT_OF_CREDITS = 20

class BotEventBase(SQLModel):
    old_state: BotStates
    new_state: BotStates
    event_type: BotEventTypes
    event_sub_type: Optional[BotEventSubTypes] = None
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    requested_bot_action_taken_at: Optional[datetime] = None
    bot_id: int = Field(foreign_key="bot.id")

class BotEvent(BotEventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional["Bot"] = Relationship(back_populates="bot_events")
    debug_screenshots: List["BotDebugScreenshot"] = Relationship(back_populates="bot_event")

class BotEventCreate(BotEventBase):
    pass

class BotEventRead(BotEventBase):
    id: int
    created_at: datetime

class BotEventUpdate(SQLModel):
    old_state: Optional[BotStates] = None
    new_state: Optional[BotStates] = None
    event_type: Optional[BotEventTypes] = None
    event_sub_type: Optional[BotEventSubTypes] = None
    metadata_: Optional[Dict[str, Any]] = None
    requested_bot_action_taken_at: Optional[datetime] = None


class BotDebugScreenshotBase(SQLModel):
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    file_url: Optional[str] = None # To store the URL of the screenshot file
    bot_event_id: int = Field(foreign_key="botevent.id")

class BotDebugScreenshot(BotDebugScreenshotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "shot_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot_event: Optional[BotEvent] = Relationship(back_populates="debug_screenshots")

class BotDebugScreenshotCreate(BotDebugScreenshotBase):
    pass

class BotDebugScreenshotRead(BotDebugScreenshotBase):
    id: int
    object_id: str
    created_at: datetime

class BotDebugScreenshotUpdate(SQLModel):
    metadata_: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None


class BotBase(SQLModel):
    name: str = Field(default="My bot", max_length=255)
    meeting_url: str = Field(max_length=511)
    meeting_uuid: Optional[str] = Field(default=None, max_length=511)
    state: BotStates = Field(default=BotStates.READY)
    settings: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    metadata_: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    first_heartbeat_timestamp: Optional[int] = None
    last_heartbeat_timestamp: Optional[int] = None
    join_at: Optional[datetime] = None
    project_id: int = Field(foreign_key="project.id")

class Bot(BotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "bot_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="bots")
    recordings: List["Recording"] = Relationship(back_populates="bot")
    participants: List["Participant"] = Relationship(back_populates="bot")
    chat_messages: List["ChatMessage"] = Relationship(back_populates="bot")
    credit_transactions: List["CreditTransaction"] = Relationship(back_populates="bot")
    bot_events: List["BotEvent"] = Relationship(back_populates="bot")
    media_requests: List["BotMediaRequest"] = Relationship(back_populates="bot")
    chat_message_requests: List["BotChatMessageRequest"] = Relationship(back_populates="bot")
    webhook_delivery_attempts: List["WebhookDeliveryAttempt"] = Relationship(back_populates="bot")
    bot_webhook_subscriptions: List["WebhookSubscription"] = Relationship(back_populates="bot")

class BotCreate(BotBase):
    pass

class BotRead(BotBase):
    id: int
    object_id: str
    created_at: datetime
    updated_at: datetime

class BotUpdate(SQLModel):
    name: Optional[str] = None
    meeting_url: Optional[str] = None
    meeting_uuid: Optional[str] = None
    state: Optional[BotStates] = None
    settings: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = None
    first_heartbeat_timestamp: Optional[int] = None
    last_heartbeat_timestamp: Optional[int] = None
    join_at: Optional[datetime] = None
    project_id: Optional[int] = None


class ParticipantBase(SQLModel):
    uuid: str = Field(max_length=255)
    user_uuid: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    is_the_bot: bool = Field(default=False)
    bot_id: int = Field(foreign_key="bot.id")

class Participant(ParticipantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "par_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional[Bot] = Relationship(back_populates="participants")
    events: List["ParticipantEvent"] = Relationship(back_populates="participant")
    chat_messages: List["ChatMessage"] = Relationship(back_populates="participant")
    utterances: List["Utterance"] = Relationship(back_populates="participant")

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantRead(ParticipantBase):
    id: int
    object_id: str
    created_at: datetime
    updated_at: datetime

class ParticipantUpdate(SQLModel):
    uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_the_bot: Optional[bool] = None


class ParticipantEventTypes(int, Enum):
    JOIN = 1
    LEAVE = 2

class ParticipantEventBase(SQLModel):
    event_type: ParticipantEventTypes
    event_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    timestamp_ms: int
    participant_id: int = Field(foreign_key="participant.id")

class ParticipantEvent(ParticipantEventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "pe_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    participant: Optional[Participant] = Relationship(back_populates="events")

class ParticipantEventCreate(ParticipantEventBase):
    pass

class ParticipantEventRead(ParticipantEventBase):
    id: int
    object_id: str
    created_at: datetime

class ParticipantEventUpdate(SQLModel):
    event_type: Optional[ParticipantEventTypes] = None
    event_data: Optional[Dict[str, Any]] = None
    timestamp_ms: Optional[int] = None


class RecordingStates(int, Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3
    FAILED = 4
    PAUSED = 5

class RecordingTranscriptionStates(int, Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3
    FAILED = 4

class RecordingTypes(int, Enum):
    AUDIO_AND_VIDEO = 1
    AUDIO_ONLY = 2

class RecordingResolutions(str, Enum):
    HD_1080P = "1080p"
    HD_720P = "720p"

class TranscriptionTypes(int, Enum):
    NON_REALTIME = 1
    REALTIME = 2
    NO_TRANSCRIPTION = 3

class TranscriptionProviders(int, Enum):
    DEEPGRAM = 1
    CLOSED_CAPTION_FROM_PLATFORM = 2
    GLADIA = 3
    OPENAI = 4
    ASSEMBLY_AI = 5
    SARVAM = 6

class RecordingBase(SQLModel):
    recording_type: RecordingTypes
    transcription_type: TranscriptionTypes
    is_default_recording: bool = Field(default=False)
    state: RecordingStates = Field(default=RecordingStates.NOT_STARTED)
    transcription_state: RecordingTranscriptionStates = Field(default=RecordingTranscriptionStates.NOT_STARTED)
    transcription_failure_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    transcription_provider: Optional[TranscriptionProviders] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    first_buffer_timestamp_ms: Optional[int] = None
    file_url: Optional[str] = None # To store the URL of the recorded file (e.g., S3 URL)
    bot_id: int = Field(foreign_key="bot.id")

class Recording(RecordingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "rec_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional[Bot] = Relationship(back_populates="recordings")
    utterances: List["Utterance"] = Relationship(back_populates="recording")

class RecordingCreate(RecordingBase):
    pass

class RecordingRead(RecordingBase):
    id: int
    object_id: str
    created_at: datetime
    updated_at: datetime

class RecordingUpdate(SQLModel):
    recording_type: Optional[RecordingTypes] = None
    transcription_type: Optional[TranscriptionTypes] = None
    is_default_recording: Optional[bool] = None
    state: Optional[RecordingStates] = None
    transcription_state: Optional[RecordingTranscriptionStates] = None
    transcription_failure_data: Optional[Dict[str, Any]] = None
    transcription_provider: Optional[TranscriptionProviders] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    first_buffer_timestamp_ms: Optional[int] = None
    file_url: Optional[str] = None


class TranscriptionFailureReasons(str, Enum):
    CREDENTIALS_NOT_FOUND = "credentials_not_found"
    CREDENTIALS_INVALID = "credentials_invalid"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUDIO_UPLOAD_FAILED = "audio_upload_failed"
    TRANSCRIPTION_REQUEST_FAILED = "transcription_request_failed"
    TIMED_OUT = "timed_out"
    INTERNAL_ERROR = "internal_error"
    UTTERANCES_STILL_IN_PROGRESS_WHEN_RECORDING_TERMINATED = "utterances_still_in_progress_when_recording_terminated"


class UtteranceSources(int, Enum):
    PER_PARTICIPANT_AUDIO = 1
    CLOSED_CAPTION_FROM_PLATFORM = 2

class UtteranceAudioFormat(int, Enum):
    PCM = 1
    MP3 = 2

class UtteranceBase(SQLModel):
    audio_blob: bytes # BinaryField in Django, use bytes in SQLModel
    audio_format: Optional[UtteranceAudioFormat] = None
    timestamp_ms: int
    duration_ms: int
    transcription: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    transcription_attempt_count: int = Field(default=0)
    failure_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    source_uuid: Optional[str] = Field(default=None, unique=True, max_length=255)
    sample_rate: Optional[int] = None
    source: UtteranceSources = Field(default=UtteranceSources.PER_PARTICIPANT_AUDIO)
    recording_id: int = Field(foreign_key="recording.id")
    participant_id: int = Field(foreign_key="participant.id")

class Utterance(UtteranceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    recording: Optional["Recording"] = Relationship(back_populates="utterances")
    participant: Optional["Participant"] = Relationship(back_populates="utterances")

class UtteranceCreate(UtteranceBase):
    pass

class UtteranceRead(UtteranceBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UtteranceUpdate(SQLModel):
    audio_blob: Optional[bytes] = None
    audio_format: Optional[UtteranceAudioFormat] = None
    timestamp_ms: Optional[int] = None
    duration_ms: Optional[int] = None
    transcription: Optional[Dict[str, Any]] = None
    transcription_attempt_count: Optional[int] = None
    failure_data: Optional[Dict[str, Any]] = None
    source_uuid: Optional[str] = None
    sample_rate: Optional[int] = None
    source: Optional[UtteranceSources] = None


class CredentialTypes(int, Enum):
    DEEPGRAM = 1
    ZOOM_OAUTH = 2
    GOOGLE_TTS = 3
    GLADIA = 4
    OPENAI = 5
    ASSEMBLY_AI = 6
    SARVAM = 7
    TEAMS_BOT_LOGIN = 8

class CredentialBase(SQLModel):
    credential_type: CredentialTypes
    encrypted_data: Optional[bytes] = Field(default=None) # BinaryField in Django
    project_id: int = Field(foreign_key="project.id")

class Credential(CredentialBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="credentials")

class CredentialCreate(CredentialBase):
    pass

class CredentialRead(CredentialBase):
    id: int
    created_at: datetime
    updated_at: datetime

class CredentialUpdate(SQLModel):
    credential_type: Optional[CredentialTypes] = None
    encrypted_data: Optional[bytes] = None


class MediaBlobValidAudioContentTypes(str, Enum):
    MP3 = "audio/mp3"

class MediaBlobValidImageContentTypes(str, Enum):
    PNG = "image/png"

class MediaBlobBase(SQLModel):
    blob: bytes
    content_type: str # This will be validated against enums in service layer
    checksum: str = Field(max_length=64) # SHA-256 hash
    duration_ms: int
    project_id: int = Field(foreign_key="project.id")

class MediaBlob(MediaBlobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "blob_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="media_blobs")
    bot_media_requests: List["BotMediaRequest"] = Relationship(back_populates="media_blob")

class MediaBlobCreate(MediaBlobBase):
    pass

class MediaBlobRead(MediaBlobBase):
    id: int
    object_id: str
    created_at: datetime

class MediaBlobUpdate(SQLModel):
    blob: Optional[bytes] = None
    content_type: Optional[str] = None
    checksum: Optional[str] = None
    duration_ms: Optional[int] = None


class TextToSpeechProviders(int, Enum):
    GOOGLE = 1

class BotMediaRequestMediaTypes(int, Enum):
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3

class BotMediaRequestStates(int, Enum):
    ENQUEUED = 1
    PLAYING = 2
    DROPPED = 3
    FINISHED = 4
    FAILED_TO_PLAY = 5

class BotMediaRequestBase(SQLModel):
    text_to_speak: Optional[str] = None
    text_to_speech_settings: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    media_url: Optional[str] = None
    media_type: BotMediaRequestMediaTypes
    state: BotMediaRequestStates = Field(default=BotMediaRequestStates.ENQUEUED)
    bot_id: int = Field(foreign_key="bot.id")
    media_blob_id: Optional[int] = Field(default=None, foreign_key="mediablob.id")

class BotMediaRequest(BotMediaRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional[Bot] = Relationship(back_populates="media_requests")
    media_blob: Optional[MediaBlob] = Relationship(back_populates="bot_media_requests")

    # Unique constraint for playing media request per bot and type will be handled in service layer

class BotMediaRequestCreate(BotMediaRequestBase):
    pass

class BotMediaRequestRead(BotMediaRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime

class BotMediaRequestUpdate(SQLModel):
    text_to_speak: Optional[str] = None
    text_to_speech_settings: Optional[Dict[str, Any]] = None
    media_url: Optional[str] = None
    media_type: Optional[BotMediaRequestMediaTypes] = None
    state: Optional[BotMediaRequestStates] = None
    media_blob_id: Optional[int] = None


class BotChatMessageRequestStates(int, Enum):
    ENQUEUED = 1
    SENT = 2
    FAILED = 3

class BotChatMessageToOptions(str, Enum):
    EVERYONE = "everyone"
    SPECIFIC_USER = "specific_user"
    EVERYONE_BUT_HOST = "everyone_but_host"

class BotChatMessageRequestBase(SQLModel):
    to_user_uuid: Optional[str] = Field(default=None, max_length=255)
    to: BotChatMessageToOptions
    message: str
    additional_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    state: BotChatMessageRequestStates = Field(default=BotChatMessageRequestStates.ENQUEUED)
    sent_at_timestamp_ms: Optional[int] = None
    failure_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    bot_id: int = Field(foreign_key="bot.id")

class BotChatMessageRequest(BotChatMessageRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional[Bot] = Relationship(back_populates="chat_message_requests")

class BotChatMessageRequestCreate(BotChatMessageRequestBase):
    pass

class BotChatMessageRequestRead(BotChatMessageRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime

class BotChatMessageRequestUpdate(SQLModel):
    to_user_uuid: Optional[str] = None
    to: Optional[BotChatMessageToOptions] = None
    message: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    state: Optional[BotChatMessageRequestStates] = None
    sent_at_timestamp_ms: Optional[int] = None
    failure_data: Optional[Dict[str, Any]] = None


class WebhookTriggerTypes(int, Enum):
    BOT_STATE_CHANGE = 1
    TRANSCRIPT_UPDATE = 2
    CHAT_MESSAGES_UPDATE = 3
    PARTICIPANT_EVENTS_JOIN_LEAVE = 4

class WebhookSecretBase(SQLModel):
    secret: Optional[bytes] = Field(default=None) # BinaryField in Django
    project_id: int = Field(foreign_key="project.id")

class WebhookSecret(WebhookSecretBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="webhook_secrets")

class WebhookSecretCreate(WebhookSecretBase):
    pass

class WebhookSecretRead(WebhookSecretBase):
    id: int
    created_at: datetime
    updated_at: datetime

class WebhookSecretUpdate(SQLModel):
    secret: Optional[bytes] = None


class WebhookSubscriptionBase(SQLModel):
    url: str
    triggers: List[WebhookTriggerTypes] = Field(default_factory=lambda: [WebhookTriggerTypes.BOT_STATE_CHANGE], sa_type=JSONB)
    is_active: bool = Field(default=True)
    project_id: int = Field(foreign_key="project.id")
    bot_id: Optional[int] = Field(default=None, foreign_key="bot.id")

class WebhookSubscription(WebhookSubscriptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "webhook_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="webhook_subscriptions")
    bot: Optional[Bot] = Relationship(back_populates="bot_webhook_subscriptions")
    webhookdelivery_attempts: List["WebhookDeliveryAttempt"] = Relationship(back_populates="webhook_subscription")

class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass

class WebhookSubscriptionRead(WebhookSubscriptionBase):
    id: int
    object_id: str
    created_at: datetime
    updated_at: datetime

class WebhookSubscriptionUpdate(SQLModel):
    url: Optional[str] = None
    triggers: Optional[List[WebhookTriggerTypes]] = None
    is_active: Optional[bool] = None


class WebhookDeliveryAttemptStatus(int, Enum):
    PENDING = 1
    SUCCESS = 2
    FAILURE = 3

class WebhookDeliveryAttemptBase(SQLModel):
    webhook_trigger_type: WebhookTriggerTypes = Field(default=WebhookTriggerTypes.BOT_STATE_CHANGE)
    idempotency_key: str = Field(unique=True, max_length=36) # UUID field in Django
    payload: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    status: WebhookDeliveryAttemptStatus = Field(default=WebhookDeliveryAttemptStatus.PENDING)
    attempt_count: int = Field(default=0)
    last_attempt_at: Optional[datetime] = None
    succeeded_at: Optional[datetime] = None
    response_body_list: List[Dict[str, Any]] = Field(default_factory=list, sa_type=JSONB)
    webhook_subscription_id: int = Field(foreign_key="webhooksubscription.id")
    bot_id: Optional[int] = Field(default=None, foreign_key="bot.id")

class WebhookDeliveryAttempt(WebhookDeliveryAttemptBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    webhook_subscription: Optional[WebhookSubscription] = Relationship(back_populates="webhookdelivery_attempts")
    bot: Optional[Bot] = Relationship(back_populates="webhook_delivery_attempts")

class WebhookDeliveryAttemptCreate(WebhookDeliveryAttemptBase):
    pass

class WebhookDeliveryAttemptRead(WebhookDeliveryAttemptBase):
    id: int
    created_at: datetime
    updated_at: datetime

class WebhookDeliveryAttemptUpdate(SQLModel):
    webhook_trigger_type: Optional[WebhookTriggerTypes] = None
    idempotency_key: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    status: Optional[WebhookDeliveryAttemptStatus] = None
    attempt_count: Optional[int] = None
    last_attempt_at: Optional[datetime] = None
    succeeded_at: Optional[datetime] = None
    response_body_list: Optional[List[Dict[str, Any]]] = None


class ChatMessageToOptions(int, Enum):
    ONLY_BOT = 1
    EVERYONE = 2

class ChatMessageBase(SQLModel):
    text: str
    to: ChatMessageToOptions
    timestamp: int
    additional_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    source_uuid: Optional[str] = Field(default=None, unique=True, max_length=255)
    bot_id: int = Field(foreign_key="bot.id")
    participant_id: int = Field(foreign_key="participant.id")

class ChatMessage(ChatMessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: str = Field(default_factory=lambda: "msg_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)), unique=True, max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    bot: Optional[Bot] = Relationship(back_populates="chat_messages")
    participant: Optional[Participant] = Relationship(back_populates="chat_messages")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    id: int
    object_id: str
    updated_at: datetime

class ChatMessageUpdate(SQLModel):
    text: Optional[str] = None
    to: Optional[ChatMessageToOptions] = None
    timestamp: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None
    source_uuid: Optional[str] = None


class CreditTransactionBase(SQLModel):
    centicredits_before: int
    centicredits_after: int
    centicredits_delta: int
    stripe_payment_intent_id: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    organization_id: int = Field(foreign_key="organization.id")
    bot_id: Optional[int] = Field(default=None, foreign_key="bot.id")
    parent_transaction_id: Optional[int] = Field(default=None, foreign_key="credittransaction.id")

class CreditTransaction(CreditTransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    organization: Optional[Organization] = Relationship(back_populates="credit_transactions")
    bot: Optional[Bot] = Relationship(back_populates="credit_transactions")
    parent_transaction: Optional["CreditTransaction"] = Relationship(back_populates="child_transactions",
                                                                      sa_relationship_kwargs={"remote_side": "CreditTransaction.id"})
    child_transactions: List["CreditTransaction"] = Relationship(back_populates="parent_transaction")

class CreditTransactionCreate(CreditTransactionBase):
    pass

class CreditTransactionRead(CreditTransactionBase):
    id: int
    created_at: datetime

class CreditTransactionUpdate(SQLModel):
    centicredits_before: Optional[int] = None
    centicredits_after: Optional[int] = None
    stripe_payment_intent_id: Optional[str] = None
    description: Optional[str] = None
    organization_id: Optional[int] = None
    bot_id: Optional[int] = None
    parent_transaction_id: Optional[int] = None


























































