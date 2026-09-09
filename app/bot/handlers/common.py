"""Umumiy handlerlar — /start, /help, til tanlash (doimiy knopka + inline picker)."""

from __future__ import annotations

from collections.abc import Callable

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.emoji import change_lang_prefix, flag_emoji
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


async def _send_language_picker(message: Message, prompt_lang: Lang) -> None:
    """Til tanlash: premium 🌍 + har til premium bayrog'i bilan, + inline picker.

    Custom emoji rad etilsa (CUSTOM_EMOJI_INVALID) oddiy emojilar bilan qayta yuboriladi.
    """
    prompt = t("choose_language", prompt_lang)
    keyboard = language_inline_keyboard()
    lines = [f"{change_lang_prefix()} <b>{prompt}</b>", ""]
    lines += [f"{flag_emoji(info.code)} {info.native_name}" for info in LANGUAGES]
    try:
        await message.answer("\n".join(lines), reply_markup=keyboard)
    except TelegramBadRequest:
        plain = [f"🌐 <b>{prompt}</b>", ""]
        plain += [f"{info.flag} {info.native_name}" for info in LANGUAGES]
        await message.answer("\n".join(plain), reply_markup=keyboard)


@router.message(CommandStart())
async def cmd_start(message: Message, lang: Lang | None) -> None:
    # Til hali tanlanmagan bo'lsa — avval tilni so'raymiz (birinchi qadam).
    if lang is None:
        await _send_language_picker(message, DEFAULT_LANG)
        return
    await message.answer(t("start_welcome", lang), reply_markup=main_reply_keyboard(lang))


@router.message(F.text.in_(_CHANGE_LANG_LABELS))
async def on_change_language_button(message: Message, lang: Lang | None) -> None:
    # Doimiy pastki knopka bosildi — til tanlash pickerini ko'rsatamiz.
    await _send_language_picker(message, lang or DEFAULT_LANG)


@router.callback_query(F.data.startswith(f"{LANG_CALLBACK_PREFIX}:"))
async def on_language_selected(callback: CallbackQuery, session: AsyncSession) -> None:
    assert callback.data is not None
    chosen: Lang = parse_lang(callback.data.split(":", 1)[1])

    await set_language(session, callback.from_user.id, chosen)
    await callback.answer()

    # Tanlangan YANGI tilda javob beramiz (middleware eski tilni ko'rgan edi).
    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_text(
                f"{flag_emoji(chosen)} {t('language_changed', chosen)}"
            )
        except TelegramBadRequest:
            await callback.message.edit_text(t("language_changed", chosen))
        # Doimiy knopkani yangi til yorlig'i bilan yangilash uchun xabar yuboramiz.
        await callback.message.answer(
            t("start_welcome", chosen), reply_markup=main_reply_keyboard(chosen)
        )


@router.message(Command("help"))
async def cmd_help(message: Message, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    await message.answer(t("help_text", effective), reply_markup=main_reply_keyboard(effective))
