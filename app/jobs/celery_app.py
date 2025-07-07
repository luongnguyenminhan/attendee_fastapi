from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "attendee_fastapi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.jobs.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)

celery_app.autodiscover_tasks(["app.jobs"])

