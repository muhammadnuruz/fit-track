import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.api_client import ApiClient, ApiError
from app.emoji import (
    FALLBACK_FLAG,
    check_emoji,
    flag_emoji,
    globe_emoji,
    point_down,
    welcome_emojis,
)
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang, parse_lang, t
from app.keyboards.language import (
    LANG_CALLBACK_PREFIX,
    change_language_labels,
    language_inline_keyboard,
    main_reply_keyboard,
)
from app.keyboards.onboarding import start_onboarding_keyboard
from app.notifications import notify_admins_new_user

router = Router(name="common")
log = logging.getLogger(__name__)

_CHANGE_LANG_LABELS = change_language_labels()


async def send_language_picker(message: Message) -> None:
    keyboard = language_inline_keyboard()
    lines = [
        f"{flag_emoji(info.code)} {t('choose_language', info.code).rstrip(': ')} {point_down()}"
        for info in LANGUAGES
    ]
    try:
        await message.answer("\n".join(lines), reply_markup=keyboard)
    except TelegramBadRequest:
        plain = [
            f"{info.flag} {t('choose_language', info.code).rstrip(': ')} 👇" for info in LANGUAGES
        ]
        await message.answer("\n".join(plain), reply_markup=keyboard)


async def send_welcome(message: Message, lang: Lang) -> None:
    keyboard = main_reply_keyboard(lang)
    try:
        await message.answer(t("start_welcome", lang, **welcome_emojis()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(
            t("start_welcome", lang, wave="👋", smile="😊", salad="🥗", muscle="💪", point="👇"),
            reply_markup=keyboard,
        )


async def _send_onboarding_cta(message: Message, lang: Lang) -> None:
    keyboard = start_onboarding_keyboard(lang)
    try:
        await message.answer(t("onboarding_cta", lang, point=point_down()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(t("onboarding_cta", lang, point="👇"), reply_markup=keyboard)


async def _is_registered(api: ApiClient, telegram_id: int) -> bool:
    try:
        return await api.get_profile(telegram_id) is not None
    except ApiError:
        log.warning("profile lookup failed for %s", telegram_id)
        return True


@router.message(CommandStart())
async def cmd_start(message: Message, lang: Lang | None, api: ApiClient) -> None:
    if message.from_user is None:
        return
    if lang is None:
        await send_language_picker(message)
        return
    await send_welcome(message, lang)
    if not await _is_registered(api, message.from_user.id):
        await _send_onboarding_cta(message, lang)


@router.message(F.text.in_(_CHANGE_LANG_LABELS))
async def on_change_language_button(message: Message) -> None:
    await send_language_picker(message)


@router.callback_query(F.data.startswith(f"{LANG_CALLBACK_PREFIX}:"))
async def on_language_selected(callback: CallbackQuery, api: ApiClient) -> None:
    assert callback.data is not None
    chosen: Lang = parse_lang(callback.data.split(":", 1)[1])
    telegram_id = callback.from_user.id

    try:
        is_new = await api.get_language(telegram_id) is None
        await api.set_language(telegram_id, chosen)
    except ApiError:
        await callback.answer(t("service_unavailable", DEFAULT_LANG), show_alert=True)
        return
    await callback.answer()

    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_text(
                t("language_changed", chosen, check=check_emoji(), flag=flag_emoji(chosen))
            )
        except TelegramBadRequest:
            await callback.message.edit_text(
                t("language_changed", chosen, check="✅", flag=FALLBACK_FLAG[chosen])
            )
        await send_welcome(callback.message, chosen)
        if is_new and callback.bot is not None:
            await notify_admins_new_user(callback.bot, callback.from_user, chosen)


@router.message(Command("help"))
async def cmd_help(message: Message, lang: Lang | None) -> None:
    if message.from_user is None:
        return
    effective = lang or DEFAULT_LANG
    keyboard = main_reply_keyboard(effective)
    try:
        await message.answer(t("help_text", effective, globe=globe_emoji()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(t("help_text", effective, globe="🌐"), reply_markup=keyboard)
