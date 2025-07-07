from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.users.models.user_model import User
from app.core.base_model import APIResponse
from app.utils.security import get_current_user

router = APIRouter(tags=["Jobs"])


@router.get("/", summary="Get jobs")
@handle_exceptions
async def get_jobs(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> APIResponse:
    """Get jobs list - placeholder implementation"""
    return APIResponse.success(
        data={"jobs": [], "total": 0, "page": page, "size": size},
        message="jobs.messages.retrieved_successfully",
    )


@router.get("/{job_id}", summary="Get job by ID")
@handle_exceptions
async def get_job(
    job_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    """Get job by ID - placeholder implementation"""
    return APIResponse.success(
        data={"job_id": job_id, "status": "pending"},
        message="jobs.messages.retrieved_successfully",
    )
