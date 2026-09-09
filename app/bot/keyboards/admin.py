from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import emoji

STATS_BTN = "Statistics"
BROADCAST_BTN = "Broadcast"
BACK_MAIN_MENU = "Main Menu"
BACK_ADMIN_MENU = "Admin Menu"


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=STATS_BTN, icon_custom_emoji_id=emoji.STATISTICS_EMOJI_ID)
    builder.button(text=BROADCAST_BTN, icon_custom_emoji_id=emoji.BROADCAST_EMOJI_ID)
    builder.button(text=BACK_MAIN_MENU, icon_custom_emoji_id=emoji.BACK_EMOJI_ID)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, is_persistent=True)
