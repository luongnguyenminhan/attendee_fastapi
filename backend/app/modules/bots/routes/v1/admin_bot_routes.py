import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.base_model import PaginationParams
from app.core.database import get_session
from app.exceptions.handlers import handle_exceptions
from app.modules.bots.repository.bot_repo import BotRepo


class AsyncSessionWrapper:
    """Wrapper to make sync session compatible with async repository interface"""

    def __init__(self, sync_session: Session):
        self._session = sync_session

    def __getattr__(self, name):
        """Delegate all attributes to the wrapped session"""
        attr = getattr(self._session, name)
        if name == "execute":
            return self._async_execute
        return attr

    async def _async_execute(self, statement):
        """Convert sync execute to async"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.execute, statement)

    async def commit(self):
        """Async wrapper for commit"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.commit)

    async def rollback(self):
        """Async wrapper for rollback"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.rollback)

    async def close(self):
        """Async wrapper for close"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.close)

    async def flush(self):
        """Async wrapper for flush"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.flush)

    async def refresh(self, instance):
        """Async wrapper for refresh"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._session.refresh, instance)


async def get_async_session():
    """Get async-compatible session for admin routes"""
    async for session in get_session():
        yield AsyncSessionWrapper(session)


# Dependency to get current admin user (simplified for now)
async def get_current_admin_user():
    return {"username": "admin", "email": "admin@attendee.dev", "is_admin": True}


router = APIRouter(prefix="/admin/bots", tags=["Admin - Bots"])


@router.get("/", summary="Admin - Get all bots with advanced filtering")
@handle_exceptions
async def admin_get_bots(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    state: str = Query(None),
    project_id: str = Query(None),
    organization_id: str = Query(None),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get paginated bots with comprehensive filtering and logging"""

    print("=== ADMIN GET BOTS REQUEST ===")
    print(f"Page: {page}, Page size: {page_size}")
    print(f"Search: {search}")
    print(f"State filter: {state}")
    print(f"Project ID: {project_id}")
    print(f"Organization ID: {organization_id}")
    print(f"Admin user: {current_user}")
    print("===============================")

    try:
        repo = BotRepo(db)
        pagination = PaginationParams(page=page, limit=page_size)

        print("=== FILTERING BOTS ===")
        if project_id:
            print(f"Getting bots for project: {project_id}")
            bots_page = await repo.get_bots_by_project(project_id=project_id, pagination=pagination, state=state, search=search)
        else:
            print("Getting all bots with filters")
            bots_page = await repo.get_all_bots_admin(
                pagination=pagination,
                state=state,
                search=search,
                organization_id=organization_id,
            )

        print(f"✅ Found {len(bots_page.items)} bots (total: {bots_page.total})")

        # Convert to response format
        bot_responses = []
        for bot in bots_page.items:
            bot_data = {
                "id": str(bot.id),
                "name": bot.name,
                "meeting_url": bot.meeting_url,
                "project_id": str(bot.project_id) if bot.project_id else None,
                "state": bot.state,
                "meeting_uuid": bot.meeting_uuid,
                "join_at": bot.join_at.isoformat() if bot.join_at else None,
                "joined_at": bot.joined_at.isoformat() if bot.joined_at else None,
                "left_at": bot.left_at.isoformat() if bot.left_at else None,
                "created_at": bot.create_date.isoformat() if bot.create_date else None,
                "updated_at": bot.update_date.isoformat() if bot.update_date else None,
            }
            bot_responses.append(bot_data)

        response_data = {
            "bots": bot_responses,
            "total": bots_page.total,
            "page": page,
            "page_size": page_size,
            "total_pages": bots_page.total_pages,
        }

        print(f"✅ Response prepared with {len(bot_responses)} bots")
        print("🎉 SUCCESS: Returning admin bots list")
        print("=========================================")

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"❌ ADMIN GET BOTS ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return JSONResponse(content={"error": f"Failed to get bots: {str(e)}"}, status_code=500)


@router.get("/stats", summary="Admin - Get bot statistics")
@handle_exceptions
async def admin_get_bot_stats(
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get comprehensive bot statistics"""

    print("=== ADMIN GET BOT STATS ===")
    print(f"Admin user: {current_user}")
    print("============================")

    try:
        repo = BotRepo(db)
        stats = await repo.get_bot_stats_admin()

        print("✅ Bot stats retrieved:")
        print(f"   - Total bots: {stats.get('total_count', 0)}")
        print(f"   - Active bots: {stats.get('joined_count', 0)}")
        print(f"   - Completed bots: {stats.get('completed_count', 0)}")

        return JSONResponse(content={"success": True, "data": stats}, status_code=200)

    except Exception as e:
        print(f"❌ GET BOT STATS ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to get bot stats: {str(e)}"},
            status_code=500,
        )


@router.get("/{bot_id}", summary="Admin - Get bot details")
@handle_exceptions
async def admin_get_bot_details(
    bot_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get detailed bot information"""

    print("=== ADMIN GET BOT DETAILS ===")
    print(f"Bot ID: {bot_id}")
    print(f"Admin user: {current_user}")
    print("==============================")

    try:
        repo = BotRepo(db)
        bot = await repo.get_bot_by_id(bot_id)

        if not bot:
            print(f"❌ BOT NOT FOUND: {bot_id}")
            return JSONResponse(content={"success": False, "message": "Bot not found"}, status_code=404)

        bot_data = {
            "id": str(bot.id),
            "name": bot.name,
            "meeting_url": bot.meeting_url,
            "project_id": str(bot.project_id) if bot.project_id else None,
            "state": bot.state,
            "meeting_uuid": bot.meeting_uuid,
            "settings": bot.settings,
            "join_at": bot.join_at.isoformat() if bot.join_at else None,
            "joined_at": bot.joined_at.isoformat() if bot.joined_at else None,
            "left_at": bot.left_at.isoformat() if bot.left_at else None,
            "created_at": bot.create_date.isoformat() if bot.create_date else None,
            "updated_at": bot.update_date.isoformat() if bot.update_date else None,
        }

        print(f"✅ Bot details retrieved: {bot.name}")
        return JSONResponse(content={"success": True, "data": bot_data}, status_code=200)

    except Exception as e:
        print(f"❌ GET BOT DETAILS ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to get bot: {str(e)}"},
            status_code=500,
        )


@router.post("/{bot_id}/force-leave", summary="Admin - Force bot to leave meeting")
@handle_exceptions
async def admin_force_leave_bot(
    bot_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to force bot to leave meeting"""

    print("=== ADMIN FORCE LEAVE BOT ===")
    print(f"Bot ID: {bot_id}")
    print(f"Admin user: {current_user}")
    print("==============================")

    try:
        repo = BotRepo(db)
        bot = await repo.leave_meeting(bot_id)

        print(f"✅ Bot forced to leave: {bot.name}")
        return JSONResponse(
            content={
                "success": True,
                "message": f"Bot {bot.name} forced to leave meeting",
            },
            status_code=200,
        )

    except Exception as e:
        print(f"❌ FORCE LEAVE BOT ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to force leave bot: {str(e)}",
            },
            status_code=500,
        )


@router.delete("/{bot_id}", summary="Admin - Delete bot")
@handle_exceptions
async def admin_delete_bot(
    bot_id: str,
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to delete bot"""

    print("=== ADMIN DELETE BOT ===")
    print(f"Bot ID: {bot_id}")
    print(f"Admin user: {current_user}")
    print("=========================")

    try:
        repo = BotRepo(db)
        await repo.delete_bot(bot_id)

        print(f"✅ Bot deleted: {bot_id}")
        return JSONResponse(
            content={"success": True, "message": "Bot deleted successfully"},
            status_code=200,
        )

    except Exception as e:
        print(f"❌ DELETE BOT ERROR: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Failed to delete bot: {str(e)}"},
            status_code=500,
        )


@router.get("/{bot_id}/events", summary="Admin - Get bot events")
@handle_exceptions
async def admin_get_bot_events(
    bot_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSessionWrapper = Depends(get_async_session),
    current_user=Depends(get_current_admin_user),
):
    """Admin endpoint to get bot events"""

    print("=== ADMIN GET BOT EVENTS ===")
    print(f"Bot ID: {bot_id}")
    print(f"Limit: {limit}")
    print(f"Admin user: {current_user}")
    print("=============================")

    try:
        repo = BotRepo(db)
        events = await repo.get_bot_events(bot_id, limit)

        print(f"✅ Found {len(events)} bot events")
        return JSONResponse(
            content={"success": True, "data": {"events": events, "total": len(events)}},
            status_code=200,
        )

    except Exception as e:
        print(f"❌ GET BOT EVENTS ERROR: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to get bot events: {str(e)}",
            },
            status_code=500,
        )
