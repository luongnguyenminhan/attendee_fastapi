from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.jobs.tasks import add_numbers, process_meeting_recording, send_webhook_notification, transcribe_audio, join_meeting_task
from app.utils.security import get_current_user
from app.modules.users.models import User

router = APIRouter()

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class AddNumbersRequest(BaseModel):
    x: int
    y: int

class ProcessRecordingRequest(BaseModel):
    bot_id: int
    recording_data: Dict[str, Any]

class WebhookRequest(BaseModel):
    webhook_url: str
    payload: Dict[str, Any]

class TranscribeRequest(BaseModel):
    recording_id: int
    audio_file_path: str

class JoinMeetingRequest(BaseModel):
    bot_id: int
    meeting_url: str
    settings: Dict[str, Any]

@router.post("/test-add", response_model=TaskResponse)
async def test_add_task(request: AddNumbersRequest, current_user: User = Depends(get_current_user)):
    """Test Celery with simple addition task"""
    task = add_numbers.delay(request.x, request.y)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Addition task queued: {request.x} + {request.y}"
    )

@router.post("/process-recording", response_model=TaskResponse)
async def process_recording_task(request: ProcessRecordingRequest, current_user: User = Depends(get_current_user)):
    """Queue recording processing task"""
    task = process_meeting_recording.delay(request.bot_id, request.recording_data)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Recording processing task queued for bot {request.bot_id}"
    )

@router.post("/send-webhook", response_model=TaskResponse)
async def send_webhook_task(request: WebhookRequest, current_user: User = Depends(get_current_user)):
    """Queue webhook notification task"""
    task = send_webhook_notification.delay(request.webhook_url, request.payload)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Webhook notification task queued for {request.webhook_url}"
    )

@router.post("/transcribe", response_model=TaskResponse)
async def transcribe_task(request: TranscribeRequest, current_user: User = Depends(get_current_user)):
    """Queue audio transcription task"""
    task = transcribe_audio.delay(request.recording_id, request.audio_file_path)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Transcription task queued for recording {request.recording_id}"
    )

@router.post("/join-meeting", response_model=TaskResponse)
async def join_meeting_task_endpoint(request: JoinMeetingRequest, current_user: User = Depends(get_current_user)):
    """Queue meeting join task"""
    task = join_meeting_task.delay(request.bot_id, request.meeting_url, request.settings)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Meeting join task queued for bot {request.bot_id}"
    )

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a Celery task"""
    from app.jobs.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task is waiting to be processed'
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': str(task.info)
        }
    
    return response

