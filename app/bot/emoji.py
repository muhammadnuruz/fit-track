"""Telegram premium (custom) emoji yordamchisi.

MUHIM: custom emoji FAQAT xabar matnida/captionда render bo'ladi (HTML `<tg-emoji>`),
klaviatura tugmalarida EMAS — Telegram Bot API cheklovi. Shu sabab premium emoji
til tanlash XABARIDA ishlatiladi, tugmada esa oddiy matn/emoji qoladi.

Agar Telegram custom emoji id'ni qabul qilmasa (CUSTOM_EMOJI_INVALID), fallback
belgi (matndagi oddiy emoji) ko'rinadi — matn hech qachon "buzilmaydi".
"""

from __future__ import annotations

from app.i18n import Lang

# Til o'zgartirish uchun premium emoji id (foydalanuvchi bergan).
CHANGE_LANG_EMOJI_ID = "5399898266265475100"

# Har bir til bayrog'ining premium emoji id'lari (foydalanuvchi bergan).
FLAG_EMOJI_IDS: dict[Lang, str] = {
    Lang.UZ: "5449829434334912605",
    Lang.RU: "5449408995691341691",
    Lang.EN: "5228818371562190371",
}

# Premium emoji ishlamasa ko'rinadigan oddiy bayroqlar.
FALLBACK_FLAG: dict[Lang, str] = {Lang.UZ: "🇺🇿", Lang.RU: "🇷🇺", Lang.EN: "🇬🇧"}

# Pastga ishora qiluvchi premium emoji id (foydalanuvchi bergan).
POINT_DOWN_EMOJI_ID = "5470177992950946662"

# start_welcome xabaridagi premium emoji id'lari (foydalanuvchi bergan, tasdiqlangan).
WELCOME_WAVE_EMOJI_ID = "5472055112702629499"
WELCOME_SALAD_EMOJI_ID = "5264946326491134516"
WELCOME_MUSCLE_EMOJI_ID = "5471883477219549006"


def custom_emoji(emoji_id: str, fallback: str) -> str:
    """HTML `<tg-emoji>` teg — premium emoji, ishlamasa `fallback` ko'rinadi."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


def change_lang_prefix() -> str:
    """Til tanlash xabari uchun premium emoji prefiksi (fallback: 🌐)."""
    return custom_emoji(CHANGE_LANG_EMOJI_ID, "🌐")


def flag_emoji(lang: Lang) -> str:
    """Til bayrog'ining premium emojisi (fallback: oddiy bayroq)."""
    return custom_emoji(FLAG_EMOJI_IDS[lang], FALLBACK_FLAG[lang])


def point_down() -> str:
    """Pastga ishora premium emoji (fallback: 👇)."""
    return custom_emoji(POINT_DOWN_EMOJI_ID, "👇")


def welcome_emojis() -> dict[str, str]:
    """start_welcome shablonidagi {wave}/{salad}/{muscle} uchun premium emojilar."""
    return {
        "wave": custom_emoji(WELCOME_WAVE_EMOJI_ID, "👋"),
        "salad": custom_emoji(WELCOME_SALAD_EMOJI_ID, "🥗"),
        "muscle": custom_emoji(WELCOME_MUSCLE_EMOJI_ID, "💪"),
    }
