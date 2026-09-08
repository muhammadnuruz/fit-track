"""Telegram premium (custom) emoji yordamchisi.

MUHIM: custom emoji FAQAT xabar matnida/captionда render bo'ladi (HTML `<tg-emoji>`),
klaviatura tugmalarida EMAS — Telegram Bot API cheklovi. Shu sabab premium emoji
til tanlash XABARIDA ishlatiladi, tugmada esa oddiy matn/emoji qoladi.

Agar Telegram custom emoji id'ni qabul qilmasa (CUSTOM_EMOJI_INVALID), fallback
belgi (matndagi oddiy emoji) ko'rinadi — matn hech qachon "buzilmaydi".
"""

from __future__ import annotations

# Til o'zgartirish uchun premium emoji id (foydalanuvchi bergan).
CHANGE_LANG_EMOJI_ID = "5399898266265475100"


def custom_emoji(emoji_id: str, fallback: str) -> str:
    """HTML `<tg-emoji>` teg — premium emoji, ishlamasa `fallback` ko'rinadi."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


def change_lang_prefix() -> str:
    """Til tanlash xabari uchun premium emoji prefiksi (fallback: 🌐)."""
    return custom_emoji(CHANGE_LANG_EMOJI_ID, "🌐")
