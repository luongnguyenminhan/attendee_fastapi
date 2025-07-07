from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.modules.bots.models import Bot
from app.modules.bots.schemas import BotCreate, BotRead, BotUpdate
from app.modules.users.models import User
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/", response_model=BotRead, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot: BotCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    # In a real application, you'd verify project_id belongs to the current_user's organization
    db_bot = Bot.model_validate(bot)
    session.add(db_bot)
    session.commit()
    session.refresh(db_bot)
    return db_bot

@router.get("/{bot_id}", response_model=BotRead)
async def read_bot(
    bot_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    # In a real application, you'd verify bot belongs to the current_user's organization
    return bot

@router.get("/", response_model=List[BotRead])
async def read_bots(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: int = 100,
):
    # In a real application, you'd filter bots by the current_user's organization
    bots = session.exec(select(Bot).offset(offset).limit(limit)).all()
    return bots

@router.patch("/{bot_id}", response_model=BotRead)
async def update_bot(
    bot_id: int,
    bot: BotUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_bot = session.get(Bot, bot_id)
    if not db_bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    # In a real application, you'd verify bot belongs to the current_user's organization
    bot_data = bot.model_dump(exclude_unset=True)
    db_bot.sqlmodel_update(bot_data)
    session.add(db_bot)
    session.commit()
    session.refresh(db_bot)
    return db_bot

@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    # In a real application, you'd verify bot belongs to the current_user's organization
    session.delete(bot)
    session.commit()
    return {"ok": True}


