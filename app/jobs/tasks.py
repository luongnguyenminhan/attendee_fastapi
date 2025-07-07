import asyncio
from typing import Dict, Any
from app.jobs.celery_app import celery_app

@celery_app.task
def add_numbers(x: int, y: int) -> int:
    """Simple test task for Celery"""
    return x + y

@celery_app.task
def process_meeting_recording(bot_id: int, recording_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process meeting recording data"""
    # Simulate processing time
    import time
    time.sleep(2)
    
    return {
        "bot_id": bot_id,
        "status": "processed",
        "recording_data": recording_data,
        "processed_at": time.time()
    }

@celery_app.task
def send_webhook_notification(webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send webhook notification"""
    import requests
    import time
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        return {
            "status": "success",
            "status_code": response.status_code,
            "response": response.text[:500],  # Limit response size
            "sent_at": time.time()
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "sent_at": time.time()
        }

@celery_app.task
def transcribe_audio(recording_id: int, audio_file_path: str) -> Dict[str, Any]:
    """Transcribe audio from meeting recording"""
    # Simulate transcription processing
    import time
    time.sleep(5)
    
    return {
        "recording_id": recording_id,
        "status": "transcribed",
        "transcription": "This is a simulated transcription of the meeting audio.",
        "confidence": 0.95,
        "transcribed_at": time.time()
    }

@celery_app.task
def join_meeting_task(bot_id: int, meeting_url: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Task to join a meeting (simulated)"""
    import time
    time.sleep(3)  # Simulate join time
    
    return {
        "bot_id": bot_id,
        "meeting_url": meeting_url,
        "status": "joined",
        "joined_at": time.time(),
        "settings": settings
    }

