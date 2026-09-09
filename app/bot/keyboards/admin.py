from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

STATS_BTN = "📊 Statistika"
BROADCAST_BTN = "📢 Broadcast"


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=STATS_BTN)
    builder.button(text=BROADCAST_BTN)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, is_persistent=True)
