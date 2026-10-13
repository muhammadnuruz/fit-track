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

LANG_CALLBACK_PREFIX = "lang"


def main_reply_keyboard(lang: Lang) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(
            text=t("btn_change_language", lang),
            icon_custom_emoji_id=CHANGE_LANG_EMOJI_ID,
        )
    )
    return builder.as_markup(resize_keyboard=True, is_persistent=True)


def language_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for info in LANGUAGES:
        builder.add(
            InlineKeyboardButton(
                text=info.native_name,
                callback_data=f"{LANG_CALLBACK_PREFIX}:{info.code.value}",
                icon_custom_emoji_id=FLAG_EMOJI_IDS[info.code],
            )
        )
    builder.adjust(1)
    return builder.as_markup()


def change_language_labels() -> set[str]:
    return {t("btn_change_language", info.code) for info in LANGUAGES}
