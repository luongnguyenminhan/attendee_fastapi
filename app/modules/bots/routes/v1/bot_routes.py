from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.base_model import PaginationParams
from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.bots.repository.bot_repo import BotRepo
from app.modules.bots.schemas.bot_request import (
    CreateBotRequest,
    JoinMeetingRequest,
    UpdateBotRequest,
)
from app.modules.bots.schemas.bot_response import (
    BotActionAPIResponse,
    BotActionResponse,
    BotAPIResponse,
    BotEventListAPIResponse,
    BotEventResponse,
    BotListResponse,
    BotPaginatedAPIResponse,
    BotResponse,
    BotStatsAPIResponse,
    BotStatsResponse,
)
from app.modules.users.models.user_model import User
from app.utils.security import get_current_user

router = APIRouter(tags=["Bots"])


@router.post(
    "/",
    response_model=BotAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create bot",
)
@handle_exceptions
async def create_bot(
    request: CreateBotRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotAPIResponse:
    """Create a new bot"""
    repo = BotRepo(session)

    bot = await repo.create_bot(
        name=request.name,
        meeting_url=request.meeting_url,
        project_id=request.project_id,
        meeting_uuid=request.meeting_uuid,
        settings=request.settings,
        join_at=request.join_at,
    )

    response_data = BotResponse.from_entity(bot)
    return BotAPIResponse.success(data=response_data, message="bots.messages.created_successfully")


@router.get(
    "/project/{project_id}",
    response_model=BotPaginatedAPIResponse,
    summary="Get bots by project",
)
@handle_exceptions
async def get_bots_by_project(
    project_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    state: str = Query(None),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> BotPaginatedAPIResponse:
    """Get paginated list of bots by project"""
    repo = BotRepo(session)

    pagination = PaginationParams(page=page, limit=size)

    bots_page = await repo.get_bots_by_project(project_id=project_id, pagination=pagination, state=state, search=search)

    # Convert entities to response schemas
    response_items = [BotListResponse.from_entity(bot) for bot in bots_page.items]

    bots_page.items = response_items

    return BotPaginatedAPIResponse.success(data=bots_page, message="bots.messages.retrieved_successfully")


@router.get("/{bot_id}", response_model=BotAPIResponse, summary="Get bot by ID")
@handle_exceptions
async def get_bot(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotAPIResponse:
    """Get bot by ID"""
    repo = BotRepo(session)

    bot = await repo.get_bot_by_id(bot_id)
    response_data = BotResponse.from_entity(bot)

    return BotAPIResponse.success(data=response_data, message="bots.messages.retrieved_successfully")


@router.patch("/{bot_id}", response_model=BotAPIResponse, summary="Update bot")
@handle_exceptions
async def update_bot(
    bot_id: str,
    request: UpdateBotRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotAPIResponse:
    """Update bot"""
    repo = BotRepo(session)

    bot = await repo.update_bot(
        bot_id=bot_id,
        name=request.name,
        meeting_url=request.meeting_url,
        meeting_uuid=request.meeting_uuid,
        settings=request.settings,
        join_at=request.join_at,
    )

    response_data = BotResponse.from_entity(bot)
    return BotAPIResponse.success(data=response_data, message="bots.messages.updated_successfully")


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete bot")
@handle_exceptions
async def delete_bot(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete bot (soft delete)"""
    repo = BotRepo(session)
    await repo.delete_bot(bot_id)


# Bot Actions


@router.post("/{bot_id}/join", response_model=BotActionAPIResponse, summary="Join meeting")
@handle_exceptions
async def join_meeting(
    bot_id: str,
    request: JoinMeetingRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotActionAPIResponse:
    """Make bot join meeting"""
    repo = BotRepo(session)

    old_bot = await repo.get_bot_by_id(bot_id)
    old_state = old_bot.state

    bot = await repo.join_meeting(bot_id, request.recording)

    response_data = BotActionResponse.success_action(bot, "join_meeting", old_state)
    return BotActionAPIResponse.success(data=response_data, message="bots.messages.join_requested_successfully")


@router.post("/{bot_id}/leave", response_model=BotActionAPIResponse, summary="Leave meeting")
@handle_exceptions
async def leave_meeting(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotActionAPIResponse:
    """Make bot leave meeting"""
    repo = BotRepo(session)

    old_bot = await repo.get_bot_by_id(bot_id)
    old_state = old_bot.state

    bot = await repo.leave_meeting(bot_id)

    response_data = BotActionResponse.success_action(bot, "leave_meeting", old_state)
    return BotActionAPIResponse.success(data=response_data, message="bots.messages.leave_requested_successfully")


@router.post(
    "/{bot_id}/start-recording",
    response_model=BotActionAPIResponse,
    summary="Start recording",
)
@handle_exceptions
async def start_recording(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotActionAPIResponse:
    """Start bot recording"""
    repo = BotRepo(session)

    old_bot = await repo.get_bot_by_id(bot_id)
    old_state = old_bot.state

    bot = await repo.start_recording(bot_id)

    response_data = BotActionResponse.success_action(bot, "start_recording", old_state)
    return BotActionAPIResponse.success(data=response_data, message="bots.messages.recording_started_successfully")


@router.post("/{bot_id}/heartbeat", response_model=BotAPIResponse, summary="Update heartbeat")
@handle_exceptions
async def update_heartbeat(bot_id: str, session: Annotated[Session, Depends(get_session)]) -> BotAPIResponse:
    """Update bot heartbeat - no auth required for bot heartbeat"""
    repo = BotRepo(session)

    bot = await repo.update_heartbeat(bot_id)
    response_data = BotResponse.from_entity(bot)

    return BotAPIResponse.success(data=response_data, message="bots.messages.heartbeat_updated_successfully")


@router.get("/{bot_id}/stats", response_model=BotStatsAPIResponse, summary="Get bot statistics")
@handle_exceptions
async def get_bot_stats(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BotStatsAPIResponse:
    """Get bot statistics"""
    repo = BotRepo(session)

    stats = await repo.get_bot_stats(bot_id)
    response_data = BotStatsResponse(**stats)

    return BotStatsAPIResponse.success(data=response_data, message="bots.messages.stats_retrieved_successfully")


@router.get("/{bot_id}/events", response_model=BotEventListAPIResponse, summary="Get bot events")
@handle_exceptions
async def get_bot_events(
    bot_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(100, ge=1, le=500),
) -> BotEventListAPIResponse:
    """Get bot events"""
    repo = BotRepo(session)

    events = await repo.get_bot_events(bot_id, limit)

    response_items = [BotEventResponse.from_entity(event) for event in events]

    return BotEventListAPIResponse.success(data=response_items, message="bots.messages.events_retrieved_successfully")
