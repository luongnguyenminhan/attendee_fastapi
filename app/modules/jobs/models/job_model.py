from typing import Optional, Dict, Any
from sqlmodel import Field
from sqlalchemy.dialects.postgresql import JSONB

from app.core.base_model import BaseEntity
from app.core.base_enums import BaseEnum


class JobStatus(BaseEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseEntity, table=True):
    __tablename__ = "job"

    # Core fields
    name: str = Field(max_length=255, index=True)
    job_type: str = Field(max_length=100, index=True)
    status: JobStatus = Field(default=JobStatus.PENDING, index=True)

    # Job data and results
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    result: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)
    error_message: Optional[str] = Field(default=None, max_length=1000)

    # Timing
    started_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)

    # Domain/business logic methods
    def start_job(self) -> None:
        """Start job execution"""
        self.status = JobStatus.RUNNING
        self.started_at = self.get_current_time()

    def complete_job(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Complete job successfully"""
        self.status = JobStatus.COMPLETED
        self.completed_at = self.get_current_time()
        if result:
            self.result = result

    def fail_job(self, error_message: str) -> None:
        """Fail job with error"""
        self.status = JobStatus.FAILED
        self.completed_at = self.get_current_time()
        self.error_message = error_message

    def is_finished(self) -> bool:
        """Check if job is finished"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED]

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.status.value})"
