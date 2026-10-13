from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import Language
from app.schemas.profile import ProfileIn, ProfileOut
from app.schemas.settings import LanguageIn, LanguageOut
from app.services import profile_service, settings_service

router = APIRouter(prefix="/users/{telegram_id}", tags=["users"])


@router.put("/profile", response_model=ProfileOut)
async def upsert_profile(
    telegram_id: int,
    payload: ProfileIn,
    session: AsyncSession = Depends(get_session),
) -> ProfileOut:
    return await profile_service.upsert_profile(session, telegram_id, payload)


@router.get("/profile", response_model=ProfileOut)
async def get_profile(telegram_id: int, session: AsyncSession = Depends(get_session)) -> ProfileOut:
    profile = await profile_service.get_profile(session, telegram_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/language", response_model=LanguageOut)
async def get_language(
    telegram_id: int, session: AsyncSession = Depends(get_session)
) -> LanguageOut:
    language: Language | None = await settings_service.get_language(session, telegram_id)
    if language is None:
        raise HTTPException(status_code=404, detail="Language not set")
    return LanguageOut(language=language)


@router.put("/language", response_model=LanguageOut)
async def set_language(
    telegram_id: int,
    payload: LanguageIn,
    session: AsyncSession = Depends(get_session),
) -> LanguageOut:
    language = await settings_service.set_language(session, telegram_id, payload.language)
    return LanguageOut(language=language)
