from __future__ import annotations

import structlog
from aiogram.exceptions import TelegramBadRequest
from fastapi import APIRouter, Depends, HTTPException, Request
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


async def _send_plan(
    request: Request,
    chat_id: int,
    lang: Lang,
    plan: NutritionPlan,
    body_fat_pct: float | None,
    name: str,
) -> None:
    bot = request.app.state.bot
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
    session: AsyncSession = Depends(get_session),
) -> OnboardingOut:
    try:
        init = validate_init_data(payload.init_data, settings.bot_token)
    except InitDataError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    telegram_id = init.user_id

    is_existing = await get_by_telegram_id(session, telegram_id) is not None
    action = update_from_onboarding if is_existing else create_from_onboarding

    user, plan, body_fat_pct = await action(
        session,
        telegram_id,
        name=payload.name.strip(),
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

    lang = await get_language(session, telegram_id) or parse_lang(init.language_code)
    await _send_plan(request, telegram_id, lang, plan, body_fat_pct, user.name)

    return OnboardingOut(ok=True, already=is_existing, plan=_plan_out(plan, body_fat_pct))
