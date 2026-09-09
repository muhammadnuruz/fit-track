from __future__ import annotations

import structlog
from aiogram.exceptions import TelegramBadRequest
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import MacrosOut, OnboardingIn, OnboardingOut, PlanOut
from app.api.security import InitDataError, validate_init_data
from app.bot.emoji import bodyfat_emoji, plan_emojis
from app.config import settings
from app.db.session import get_session
from app.i18n import parse_lang, t
from app.services.settings import get_language
from app.services.users import create_from_onboarding, user_exists

router = APIRouter(prefix="/api")

log = structlog.get_logger(__name__)


def _build_plan_text(lang, plan, body_fat_pct, name, *, plain: bool) -> str:
    text = t(
        "plan_ready",
        lang,
        name=name,
        kcal=plan.target_kcal,
        protein=plan.macros.protein_g,
        carb=plan.macros.carb_g,
        fat=plan.macros.fat_g,
        bmi=plan.bmi,
        tdee=plan.tdee,
        **plan_emojis(plain=plain),
    )
    if body_fat_pct is not None:
        text = f"{text}\n{t('plan_bodyfat', lang, bf=body_fat_pct, e_dna=bodyfat_emoji(plain=plain))}"
    return text


async def _send_plan(request: Request, chat_id: int, lang, plan, body_fat_pct, name) -> None:
    bot = request.app.state.bot
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=_build_plan_text(lang, plan, body_fat_pct, name, plain=False),
        )
    except TelegramBadRequest:
        # Premium emoji ishlamasa — oddiy emoji bilan qayta yuboramiz
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=_build_plan_text(lang, plan, body_fat_pct, name, plain=True),
            )
        except Exception as exc:
            log.warning("plan_send_failed", chat_id=chat_id, error=str(exc))
    except Exception as exc:
        log.warning("plan_send_failed", chat_id=chat_id, error=str(exc))


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

    if await user_exists(session, telegram_id):
        return OnboardingOut(ok=True, already=True, plan=None)

    user, plan, body_fat_pct = await create_from_onboarding(
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

    return OnboardingOut(
        ok=True,
        already=False,
        plan=PlanOut(
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
        ),
    )
