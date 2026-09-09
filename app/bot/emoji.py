from __future__ import annotations

from app.i18n import Lang

CHANGE_LANG_EMOJI_ID = "5399898266265475100"

FLAG_EMOJI_IDS: dict[Lang, str] = {
    Lang.UZ: "5449829434334912605",
    Lang.RU: "5449408995691341691",
    Lang.EN: "5228818371562190371",
}

FALLBACK_FLAG: dict[Lang, str] = {Lang.UZ: "🇺🇿", Lang.RU: "🇷🇺", Lang.EN: "🇬🇧"}

POINT_DOWN_EMOJI_ID = "5470177992950946662"

WELCOME_WAVE_EMOJI_ID = "5472055112702629499"
WELCOME_SALAD_EMOJI_ID = "5264946326491134516"
WELCOME_MUSCLE_EMOJI_ID = "5471883477219549006"


def custom_emoji(emoji_id: str, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


CHECK_EMOJI_ID = "5852871561983299073"


def check_emoji() -> str:
    """Tasdiq belgisi premium emoji (fallback: ✅)."""
    return custom_emoji(CHECK_EMOJI_ID, "✅")


def globe_emoji() -> str:
    """Globe premium emoji (fallback: 🌐)."""
    return custom_emoji(CHANGE_LANG_EMOJI_ID, "🌐")


def flag_emoji(lang: Lang) -> str:
    return custom_emoji(FLAG_EMOJI_IDS[lang], FALLBACK_FLAG[lang])


def point_down() -> str:
    return custom_emoji(POINT_DOWN_EMOJI_ID, "👇")


def welcome_emojis() -> dict[str, str]:
    return {
        "wave": custom_emoji(WELCOME_WAVE_EMOJI_ID, "👋"),
        "salad": custom_emoji(WELCOME_SALAD_EMOJI_ID, "🥗"),
        "muscle": custom_emoji(WELCOME_MUSCLE_EMOJI_ID, "💪"),
    }
