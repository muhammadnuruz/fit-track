"""Umumiy handlerlar — /start, /language, /help va til tanlash callback'i."""

from __future__ import annotations

from collections.abc import Callable

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.language import LANG_CALLBACK_PREFIX, language_keyboard
from app.i18n import Lang, parse_lang, t
from app.services.settings import set_language

router = Router(name="common")

# Middleware'dan keladigan tarjima yordamchisi tipi: _("kalit", **kwargs)
Translator = Callable[..., str]


async def _show_welcome(message: Message, translate: Translator) -> None:
    await message.answer(translate("start_welcome"))


@router.message(CommandStart())
async def cmd_start(message: Message, lang: Lang | None, _: Translator) -> None:
    # Til hali tanlanmagan bo'lsa — avval tilni so'raymiz (SPEC: /start da birinchi qadam).
    if lang is None:
        await message.answer(t("choose_language"), reply_markup=language_keyboard())
        return
    await _show_welcome(message, _)


@router.message(Command("language"))
async def cmd_language(message: Message, _: Translator) -> None:
    # Istalgan payt tilni almashtirish.
    await message.answer(_("choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith(f"{LANG_CALLBACK_PREFIX}:"))
async def on_language_selected(callback: CallbackQuery, session: AsyncSession) -> None:
    assert callback.data is not None
    code = callback.data.split(":", 1)[1]
    chosen: Lang = parse_lang(code)

    await set_language(session, callback.from_user.id, chosen)
    await callback.answer()

    # Tanlangan YANGI tilda javob beramiz (middleware eski tilni ko'rgan edi).
    if isinstance(callback.message, Message):
        await callback.message.edit_text(t("language_changed", chosen))
        await callback.message.answer(t("start_welcome", chosen))


@router.message(Command("help"))
async def cmd_help(message: Message, _: Translator) -> None:
    await message.answer(_("help_text"))
