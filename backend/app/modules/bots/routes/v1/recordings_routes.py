from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import and_, select

from app.core.base_enums import RecordingStates
from app.core.database import AsyncSession, get_session
from app.modules.bots.models import Bot, Recording
from app.modules.bots.schemas import RecordingListResponse, RecordingResponse
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("", response_model=RecordingListResponse)
async def list_recordings(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    bot_id: Optional[str] = Query(None, description="Filter by bot ID"),
    state: Optional[RecordingStates] = Query(None, description="Filter by recording state"),
    limit: int = Query(50, ge=1, le=100, description="Number of recordings to return"),
    offset: int = Query(0, ge=0, description="Number of recordings to skip"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List recordings with filtering and pagination"""

    # Build query
    query = select(Recording)

    # Add filters
    conditions = []

    if bot_id:
        conditions.append(Recording.bot_id == bot_id)

    if project_id:
        # Join with Bot to filter by project
        query = query.join(Bot)
        conditions.append(Bot.project_id == project_id)

    if state:
        conditions.append(Recording.state == state)

    # Apply conditions
    if conditions:
        query = query.where(and_(*conditions))

    # Add pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await session.exec(query)
    recordings = result.all()

    # Get total count for pagination
    count_query = select(Recording)
    if conditions:
        if project_id:
            count_query = count_query.join(Bot)
        count_query = count_query.where(and_(*conditions))

    count_result = await session.exec(count_query)
    total = len(count_result.all())

    return RecordingListResponse(
        recordings=[RecordingResponse.from_orm(r) for r in recordings],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get recording by ID"""

    result = await session.exec(select(Recording).where(Recording.id == recording_id))
    recording = result.first()

    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    return RecordingResponse.from_orm(recording)


@router.get("/{recording_id}/download")
async def download_recording(
    recording_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Download recording file"""

    result = await session.exec(select(Recording).where(Recording.id == recording_id))
    recording = result.first()

    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    if not recording.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording file not available")

    # TODO: Implement actual file streaming from storage (S3, local, etc.)
    # For now, return placeholder
    def generate_file():
        yield b"Mock recording file content"

    # Determine content type based on recording type
    content_type = "video/mp4" if recording.recording_type.value == 1 else "audio/mpeg"
    filename = f"recording_{recording.object_id}.{'mp4' if recording.recording_type.value == 1 else 'mp3'}"

    return StreamingResponse(
        generate_file(),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete recording"""

    result = await session.exec(select(Recording).where(Recording.id == recording_id))
    recording = result.first()

    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    # TODO: Delete actual file from storage

    # Delete from database
    await session.delete(recording)
    await session.commit()

    return {"message": "Recording deleted successfully"}


@router.get("/{recording_id}/transcripts")
async def get_recording_transcripts(
    recording_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get transcription data for recording"""

    result = await session.exec(select(Recording).where(Recording.id == recording_id))
    recording = result.first()

    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    # Get all utterances for this recording
    utterances = recording.utterances

    transcripts = []
    for utterance in utterances:
        if utterance.has_transcription():
            transcripts.append(
                {
                    "id": utterance.object_id,
                    "timestamp_ms": utterance.timestamp_ms,
                    "duration_ms": utterance.duration_ms,
                    "speaker": utterance.get_speaker_name(),
                    "transcript": utterance.get_transcript_text(),
                    "confidence": utterance.get_confidence_score(),
                    "words": utterance.get_words(),
                }
            )

    # Sort by timestamp
    transcripts.sort(key=lambda x: x["timestamp_ms"])

    return {
        "recording_id": recording.object_id,
        "transcripts": transcripts,
        "total_utterances": len(transcripts),
    }


@router.post("/{recording_id}/retry-transcription")
async def retry_transcription(
    recording_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retry transcription for failed utterances"""

    result = await session.exec(select(Recording).where(Recording.id == recording_id))
    recording = result.first()

    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    # Find utterances that can be retried
    retry_count = 0
    for utterance in recording.utterances:
        if utterance.can_retry_transcription():
            # Queue for retry
            from app.jobs.tasks import process_utterance_task

            process_utterance_task.delay(utterance.id)
            retry_count += 1

    return {
        "message": f"Queued {retry_count} utterances for transcription retry",
        "retry_count": retry_count,
    }
