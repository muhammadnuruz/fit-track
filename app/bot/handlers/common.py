"""Umumiy handlerlar — /start, /help, til tanlash (doimiy knopka + inline picker)."""

from __future__ import annotations

from collections.abc import Callable

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.emoji import change_lang_prefix
from app.bot.keyboards.language import (
    LANG_CALLBACK_PREFIX,
    change_language_labels,
    language_inline_keyboard,
    main_reply_keyboard,
)
from app.i18n import DEFAULT_LANG, Lang, parse_lang, t
from app.services.settings import set_language

router = Router(name="common")

# Middleware'dan keladigan tarjima yordamchisi tipi: _("kalit", **kwargs)
Translator = Callable[..., str]

# Barcha tillardagi "Tilni o'zgartirish" knopka matnlari (bir marta hisoblanadi).
_CHANGE_LANG_LABELS = change_language_labels()


async def _send_language_picker(message: Message, prompt_lang: Lang) -> None:
    """Til tanlash xabari (premium emoji bilan) + inline picker yuboradi.

    Agar Telegram custom emoji id'ni rad etsa (bot unga kira olmasa), oddiy 🌐
    bilan qayta yuboriladi — /start hech qachon buzilmaydi.
    """
    prompt = t("choose_language", prompt_lang)
    keyboard = language_inline_keyboard()
    try:
        await message.answer(f"{change_lang_prefix()} {prompt}", reply_markup=keyboard)
    except TelegramBadRequest:
        await message.answer(f"🌐 {prompt}", reply_markup=keyboard)


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
        await callback.message.edit_text(t("language_changed", chosen))
        # Doimiy knopkani yangi til yorlig'i bilan yangilash uchun xabar yuboramiz.
        await callback.message.answer(
            t("start_welcome", chosen), reply_markup=main_reply_keyboard(chosen)
        )


@router.message(Command("help"))
async def cmd_help(message: Message, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    await message.answer(t("help_text", effective), reply_markup=main_reply_keyboard(effective))
