"""Umumiy handlerlar — /start, /help. Onboarding Bosqich 0 da to'ldiriladi."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 <b>FitTrack</b> ga xush kelibsiz!\n\n"
        "Men sizga makros (BJU) hisoblab, tana tarkibingizni "
        "o'zgartirishga yordam beraman — mahalliy taomlarni ham bilaman.\n\n"
        "Boshlash uchun /help ni bosing.\n"
        "<i>(Onboarding oqimi keyingi bosqichda ulanadi.)</i>"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Buyruqlar:</b>\n"
        "/start — boshlash\n"
        "/help — yordam\n\n"
        "Tez orada: profil sozlash, ovqat loglash, haftalik check-in."
    )
