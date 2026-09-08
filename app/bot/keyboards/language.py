"""Til tanlash inline klaviaturasi."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n.languages import LANGUAGES

# Callback data prefiksi:  "lang:uz"
LANG_CALLBACK_PREFIX = "lang"


def language_keyboard() -> InlineKeyboardMarkup:
    """Har bir qo'llab-quvvatlanadigan til uchun bitta tugma (bayroq + nom)."""
    builder = InlineKeyboardBuilder()
    for info in LANGUAGES:
        builder.button(
            text=f"{info.flag} {info.native_name}",
            callback_data=f"{LANG_CALLBACK_PREFIX}:{info.code.value}",
        )
    builder.adjust(1)  # har bir til alohida qatorda
    return builder.as_markup()
