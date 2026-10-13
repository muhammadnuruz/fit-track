from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.admin import StatsOut, TelegramIdsOut
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=StatsOut)
async def stats(session: AsyncSession = Depends(get_session)) -> StatsOut:
    return await admin_service.get_stats(session)


@router.get("/telegram-ids", response_model=TelegramIdsOut)
async def telegram_ids(session: AsyncSession = Depends(get_session)) -> TelegramIdsOut:
    return TelegramIdsOut(telegram_ids=await admin_service.list_telegram_ids(session))


@router.delete("/users/{telegram_id}", status_code=204)
async def delete_user(telegram_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    if not await admin_service.delete_user(session, telegram_id):
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)
