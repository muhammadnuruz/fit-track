from __future__ import annotations

import time

import structlog
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import MacrosOut, OnboardingIn, OnboardingOut, PlanOut
from app.api.security import InitDataError, validate_init_data
from app.bot.keyboards.language import main_reply_keyboard
from app.config import settings
from app.core.formulas import NutritionPlan
from app.db.session import get_session
from app.i18n import Lang, parse_lang
from app.services.plan_message import build_plan_text
from app.services.settings import get_language
from app.services.users import (
    create_from_onboarding,
    get_by_telegram_id,
    update_from_onboarding,
)

router = APIRouter(prefix="/api")

log = structlog.get_logger(__name__)

# Oddiy per-user rate-limit (bir instans uchun). Ko'p-replica'da Redis'ga ko'chirish kerak.
_last_onboard: dict[int, float] = {}


def _rate_limited(telegram_id: int) -> bool:
    now = time.monotonic()
    last = _last_onboard.get(telegram_id, 0.0)
    if now - last < settings.onboarding_min_interval_seconds:
        return True
    _last_onboard[telegram_id] = now
    # Davriy tozalash (xotira sizishining oldini olish)
    if len(_last_onboard) % 1000 == 0:
        cutoff = now - max(settings.onboarding_min_interval_seconds * 5, 300)
        for uid in [u for u, ts in _last_onboard.items() if ts < cutoff]:
            del _last_onboard[uid]
    return False


async def _send_plan(
    bot: Bot,
    chat_id: int,
    lang: Lang,
    plan: NutritionPlan,
    body_fat_pct: float | None,
    name: str,
) -> None:
    # Reja xabari bilan birga main menu (Kunlik normam tugmasi) chiqadi
    keyboard = main_reply_keyboard(lang, has_plan=True)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=build_plan_text(lang, plan, body_fat_pct, name, plain=False),
            reply_markup=keyboard,
        )
    except TelegramBadRequest:
        # Premium emoji ishlamasa — oddiy emoji bilan qayta yuboramiz
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=build_plan_text(lang, plan, body_fat_pct, name, plain=True),
                reply_markup=keyboard,
            )
        except Exception as exc:
            log.warning("plan_send_failed", chat_id=chat_id, error=str(exc))
    except Exception as exc:
        log.warning("plan_send_failed", chat_id=chat_id, error=str(exc))


def _plan_out(plan: NutritionPlan, body_fat_pct: float | None) -> PlanOut:
    return PlanOut(
        bmr=plan.bmr,
        tdee=plan.tdee,
        target_kcal=plan.target_kcal,
        bmi=plan.bmi,
        body_fat_pct=body_fat_pct,
        macros=MacrosOut(
            kcal=plan.macros.kcal,
            protein_g=plan.macros.protein_g,
            carb_g=plan.macros.carb_g,
            fat_g=plan.macros.fat_g,
        ),
    )


@router.post("/onboarding", response_model=OnboardingOut)
async def onboarding(
    payload: OnboardingIn,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> OnboardingOut:
    try:
        init = validate_init_data(
            payload.init_data,
            settings.bot_token,
            max_age_seconds=settings.init_data_max_age_seconds,
        )
    except InitDataError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    telegram_id = init.user_id

    if _rate_limited(telegram_id):
        raise HTTPException(status_code=429, detail="Juda tez-tez. Biroz kuting.")

    name = payload.name.strip()
    is_existing = await get_by_telegram_id(session, telegram_id) is not None
    action = update_from_onboarding if is_existing else create_from_onboarding
    try:
        user, plan, body_fat_pct = await action(
            session,
            telegram_id,
            name=name,
            gender=payload.gender,
            age=payload.age,
            height_cm=payload.height_cm,
            weight_kg=payload.weight_kg,
            activity=payload.activity,
            goal=payload.goal,
            waist_cm=payload.waist_cm,
            neck_cm=payload.neck_cm,
            hip_cm=payload.hip_cm,
        )
        await session.commit()
    except IntegrityError:
        # TOCTOU: parallel so'rov userni yaratib ulgurdi → update qilib qayta urinamiz.
        await session.rollback()
        user, plan, body_fat_pct = await update_from_onboarding(
            session,
            telegram_id,
            name=name,
            gender=payload.gender,
            age=payload.age,
            height_cm=payload.height_cm,
            weight_kg=payload.weight_kg,
            activity=payload.activity,
            goal=payload.goal,
            waist_cm=payload.waist_cm,
            neck_cm=payload.neck_cm,
            hip_cm=payload.hip_cm,
        )
        await session.commit()
        is_existing = True

    lang = await get_language(session, telegram_id) or parse_lang(init.language_code)
    # Telegram xabarini javob yo'lidan chiqaramiz — HTTP javob kechikmaydi.
    bot: Bot = request.app.state.bot
    background_tasks.add_task(
        _send_plan, bot, telegram_id, lang, plan, body_fat_pct, user.name
    )

    return OnboardingOut(ok=True, already=is_existing, plan=_plan_out(plan, body_fat_pct))
