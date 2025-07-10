import enum
from enum import Enum
from typing import Any


class BaseEnum(Enum):
    """Base enum class with automatic value checking"""

    def __contains__(self, value: Any) -> bool:
        """Check if value is in enum"""
        return value in [item.value for item in self.__class__]

    @classmethod
    def values(cls):
        """Get all enum values"""
        return [item.value for item in cls]

    @classmethod
    def names(cls):
        """Get all enum names"""
        return [item.name for item in cls]

    @classmethod
    def items(cls):
        """Get (name, value) pairs"""
        return [(item.name, item.value) for item in cls]

    @classmethod
    def from_value(cls, value: Any):
        """Get enum item from value"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

    def __str__(self) -> str:
        return str(self.value)


class BotStates(enum.IntEnum):
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


class BotEventTypes(enum.IntEnum):
    JOIN_REQUESTED = 1
    BOT_JOINED_MEETING = 2
    RECORDING_STARTED = 3
    RECORDING_STOPPED = 4
    POST_PROCESSING_COMPLETED = 5
    FATAL_ERROR = 6
    STAGED = 7
    RECORDING_PAUSED = 8
    RECORDING_RESUMED = 9


class BotEventSubTypes(enum.IntEnum):
    FATAL_ERROR_MEETING_NOT_FOUND = 1
    FATAL_ERROR_GENERIC = 2
    FATAL_ERROR_OUT_OF_CREDITS = 3
    FATAL_ERROR_WAITING_ROOM_TIMEOUT = 4


class RecordingStates(enum.IntEnum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3
    FAILED = 4
    PAUSED = 5


class RecordingTranscriptionStates(enum.IntEnum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3
    FAILED = 4


class RecordingTypes(enum.IntEnum):
    AUDIO_AND_VIDEO = 1
    AUDIO_ONLY = 2


class TranscriptionTypes(enum.IntEnum):
    NON_REALTIME = 1
    REALTIME = 2
    NO_TRANSCRIPTION = 3


class TranscriptionProviders(enum.IntEnum):
    DEEPGRAM = 1
    CLOSED_CAPTION_FROM_PLATFORM = 2
    GLADIA = 3
    OPENAI = 4
    ASSEMBLY_AI = 5
    SARVAM = 6


class MeetingTypes(enum.IntEnum):
    ZOOM = 1
    GOOGLE_MEET = 2
    TEAMS = 3


class CredentialTypes(enum.IntEnum):
    DEEPGRAM = 1
    ZOOM_OAUTH = 2
    GOOGLE_TEXT_TO_SPEECH = 3
    GLADIA = 4
    OPENAI = 5
    ASSEMBLY_AI = 6
    SARVAM = 7


class WebhookTriggerTypes(enum.IntEnum):
    BOT_STATE_CHANGE = 1
    TRANSCRIPT_UPDATE = 2
    CHAT_MESSAGES_UPDATE = 3
    PARTICIPANT_EVENTS_JOIN_LEAVE = 4


class WebhookDeliveryAttemptStatus(enum.IntEnum):
    PENDING = 1
    SUCCESS = 2
    FAILURE = 3


class ParticipantEventTypes(enum.IntEnum):
    JOIN = 1
    LEAVE = 2


class ChatMessageToOptions(enum.IntEnum):
    EVERYONE = 1
    ONLY_BOT = 2


class RealtimeTriggerTypes(enum.IntEnum):
    REALTIME_AUDIO_MIXED = 1
    REALTIME_AUDIO_BOT_OUTPUT = 2


class TranscriptionFailureReasons(enum.Enum):
    CREDENTIALS_NOT_FOUND = "credentials_not_found"
    CREDENTIALS_INVALID = "credentials_invalid"
    AUDIO_UPLOAD_FAILED = "audio_upload_failed"
    TRANSCRIPTION_REQUEST_FAILED = "transcription_request_failed"
    TIMED_OUT = "timed_out"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_ERROR = "internal_error"


class RecordingFormats(enum.Enum):
    MP4 = "mp4"
    MP3 = "mp3"


class BotMediaRequestStates(enum.IntEnum):
    PENDING = 1
    SUCCESS = 2
    FAILURE = 3


class BotMediaRequestMediaTypes(enum.IntEnum):
    IMAGE = 1


class BotChatMessageRequestStates(enum.IntEnum):
    PENDING = 1
    SUCCESS = 2
    FAILURE = 3
