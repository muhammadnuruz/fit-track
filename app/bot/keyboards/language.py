from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.bot.emoji import CHANGE_LANG_EMOJI_ID, FLAG_EMOJI_IDS, PLAY_EMOJI_ID
from app.config import settings
from app.i18n import LANGUAGES, Lang, t

LANG_CALLBACK_PREFIX = "lang"


def onboarding_webapp_url(lang: Lang) -> str | None:
    base = settings.webapp_url.strip()
    if not base.startswith("https://"):
        return None
    separator = "&" if "?" in base else "?"
    return f"{base}{separator}lang={lang.value}"


def main_reply_keyboard(lang: Lang, *, show_onboarding: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    url = onboarding_webapp_url(lang) if show_onboarding else None
    if url is not None:
        builder.add(
            KeyboardButton(
                text=t("btn_start_onboarding", lang),
                icon_custom_emoji_id=PLAY_EMOJI_ID,
                web_app=WebAppInfo(url=url),
            )
        )
    builder.add(
        KeyboardButton(
            text=t("btn_change_language", lang),
            icon_custom_emoji_id=CHANGE_LANG_EMOJI_ID,
        )
    )
    builder.adjust(1)
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
