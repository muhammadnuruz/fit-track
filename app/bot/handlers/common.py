"""Umumiy handlerlar — /start, /help, til tanlash (doimiy knopka + inline picker)."""

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
)
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang, parse_lang, t
from app.services.settings import set_language

router = Router(name="common")

# Middleware'dan keladigan tarjima yordamchisi tipi: _("kalit", **kwargs)
Translator = Callable[..., str]

# Barcha tillardagi "Tilni o'zgartirish" knopka matnlari (bir marta hisoblanadi).
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
            f"{info.flag} {t('choose_language', info.code).rstrip(': ')} 👇"
            for info in LANGUAGES
        ]
        await message.answer("\n".join(plain), reply_markup=keyboard)


async def _send_welcome(message: Message, lang: Lang) -> None:
    keyboard = main_reply_keyboard(lang)
    try:
        await message.answer(t("start_welcome", lang, **welcome_emojis()), reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(
            t("start_welcome", lang, wave="👋", salad="🥗", muscle="💪"),
            reply_markup=keyboard,
        )


@router.message(CommandStart())
async def cmd_start(message: Message, lang: Lang | None) -> None:
    if lang is None:
        await _send_language_picker(message)
        return
    await _send_welcome(message, lang)


@router.message(F.text.in_(_CHANGE_LANG_LABELS))
async def on_change_language_button(message: Message, lang: Lang | None) -> None:
    await _send_language_picker(message)


@router.callback_query(F.data.startswith(f"{LANG_CALLBACK_PREFIX}:"))
async def on_language_selected(callback: CallbackQuery, session: AsyncSession) -> None:
    assert callback.data is not None
    chosen: Lang = parse_lang(callback.data.split(":", 1)[1])

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
        await _send_welcome(callback.message, chosen)


@router.message(Command("help"))
async def cmd_help(message: Message, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    try:
        await message.answer(
            t("help_text", effective, globe=globe_emoji()),
            reply_markup=main_reply_keyboard(effective),
        )
    except TelegramBadRequest:
        await message.answer(
            t("help_text", effective, globe="🌐"),
            reply_markup=main_reply_keyboard(effective),
        )
