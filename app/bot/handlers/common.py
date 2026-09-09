from __future__ import annotations

from collections.abc import Callable

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.emoji import (
    FALLBACK_FLAG,
    check_emoji,
    flag_emoji,
    globe_emoji,
    point_down,
    welcome_emojis,
)
from app.bot.keyboards.language import (
    LANG_CALLBACK_PREFIX,
    change_language_labels,
    language_inline_keyboard,
    main_reply_keyboard,
    onboarding_inline_keyboard,
)
from app.bot.notifications import notify_admins_new_user
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang, parse_lang, t
from app.services.settings import has_language, set_language
from app.services.users import user_exists

router = Router(name="common")

Translator = Callable[..., str]

_CHANGE_LANG_LABELS = change_language_labels()


async def _send_language_picker(message: Message, prompt_lang: Lang = DEFAULT_LANG) -> None:
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


async def _send_onboarding_cta(message: Message, lang: Lang) -> None:
    keyboard = onboarding_inline_keyboard(lang)
    if keyboard is None:
        return
    try:
        await message.answer(t("onboarding_cta", lang, point=point_down()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(t("onboarding_cta", lang, point="👇"), reply_markup=keyboard)


async def _send_welcome(message: Message, lang: Lang, *, show_onboarding: bool) -> None:
    keyboard = main_reply_keyboard(lang)
    try:
        await message.answer(t("start_welcome", lang, **welcome_emojis()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(
            t("start_welcome", lang, wave="👋", smile="😊", salad="🥗", muscle="💪", point="👇"),
            reply_markup=keyboard,
        )
    if show_onboarding:
        await _send_onboarding_cta(message, lang)


@router.message(CommandStart())
async def cmd_start(message: Message, lang: Lang | None, session: AsyncSession) -> None:
    if lang is None:
        await _send_language_picker(message)
        return
    show_onboarding = not await user_exists(session, message.from_user.id)
    await _send_welcome(message, lang, show_onboarding=show_onboarding)


@router.message(F.text.in_(_CHANGE_LANG_LABELS))
async def on_change_language_button(message: Message, lang: Lang | None) -> None:
    await _send_language_picker(message)


@router.callback_query(F.data.startswith(f"{LANG_CALLBACK_PREFIX}:"))
async def on_language_selected(callback: CallbackQuery, session: AsyncSession) -> None:
    assert callback.data is not None
    chosen: Lang = parse_lang(callback.data.split(":", 1)[1])

    is_new = not await has_language(session, callback.from_user.id)
    await set_language(session, callback.from_user.id, chosen)
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
        show_onboarding = not await user_exists(session, callback.from_user.id)
        await _send_welcome(callback.message, chosen, show_onboarding=show_onboarding)
        if is_new:
            await notify_admins_new_user(callback.bot, callback.from_user, chosen)


@router.message(Command("help"))
async def cmd_help(message: Message, lang: Lang | None, session: AsyncSession) -> None:
    effective = lang or DEFAULT_LANG
    show_onboarding = not await user_exists(session, message.from_user.id)
    keyboard = main_reply_keyboard(effective)
    try:
        await message.answer(t("help_text", effective, globe=globe_emoji()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(t("help_text", effective, globe="🌐"), reply_markup=keyboard)
    if show_onboarding:
        await _send_onboarding_cta(message, effective)
