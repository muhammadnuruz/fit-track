import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api_client import ApiClient, ApiError
from app.i18n import DEFAULT_LANG, Lang, t
from app.keyboards.onboarding import start_onboarding_keyboard
from app.plan_text import build_plan_text

router = Router(name="profile")
log = logging.getLogger(__name__)


@router.message(Command("plan"))
async def cmd_plan(message: Message, lang: Lang | None, api: ApiClient) -> None:
    if message.from_user is None:
        return
    effective = lang or DEFAULT_LANG
    try:
        profile = await api.get_profile(message.from_user.id)
    except ApiError:
        log.warning("plan lookup failed for %s", message.from_user.id)
        await message.answer(t("service_unavailable", effective))
        return
    if profile is None:
        await message.answer(
            t("plan_no_profile", effective),
            reply_markup=start_onboarding_keyboard(effective),
        )
        return
    await message.answer(build_plan_text(effective, profile))
