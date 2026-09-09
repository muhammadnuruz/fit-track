"""Til bilan bog'liq klaviaturalar.

- `main_reply_keyboard(lang)`  → doimiy pastki reply-knopka ("Tilni o'zgartirish").
- `language_inline_keyboard()` → til tanlash uchun 3 tilli inline picker.
"""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.bot.emoji import CHANGE_LANG_EMOJI_ID, FLAG_EMOJI_IDS
from app.i18n import LANGUAGES, Lang, t

# Inline til tanlash callback prefiksi:  "lang:uz"
LANG_CALLBACK_PREFIX = "lang"


def main_reply_keyboard(lang: Lang) -> ReplyKeyboardMarkup:
    """Doimiy pastki menyu — hozircha faqat "Tilni o'zgartirish" knopkasi.

    is_persistent=True → knopka har doim ko'rinib turadi.
    Kelajakda bu yerga boshqa asosiy knopkalar qo'shiladi.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(
            text=t("btn_change_language", lang),
            icon_custom_emoji_id=CHANGE_LANG_EMOJI_ID,
        )
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, is_persistent=True)


def language_inline_keyboard() -> InlineKeyboardMarkup:
    """Har bir til uchun bitta tugma (premium bayroq icon + o'z tilidagi nom)."""
    builder = InlineKeyboardBuilder()
    for info in LANGUAGES:
        builder.add(
            InlineKeyboardButton(
                text=info.native_name,
                callback_data=f"{LANG_CALLBACK_PREFIX}:{info.code.value}",
                icon_custom_emoji_id=FLAG_EMOJI_IDS[info.code],
            )
        )
    builder.adjust(1)  # har bir til alohida qatorda
    return builder.as_markup()


def change_language_labels() -> set[str]:
    """Barcha tillardagi "Tilni o'zgartirish" knopka matnlari (message filtri uchun)."""
    return {t("btn_change_language", info.code) for info in LANGUAGES}
