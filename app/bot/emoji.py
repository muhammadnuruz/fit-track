from __future__ import annotations

from app.i18n import Lang

CHANGE_LANG_EMOJI_ID = "5399898266265475100"

FLAG_EMOJI_IDS: dict[Lang, str] = {
    Lang.UZ: "5449829434334912605",
    Lang.RU: "5449408995691341691",
    Lang.EN: "5202196682497859879",
}

FALLBACK_FLAG: dict[Lang, str] = {Lang.UZ: "🇺🇿", Lang.RU: "🇷🇺", Lang.EN: "🇬🇧"}

POINT_DOWN_EMOJI_ID = "5470177992950946662"
PLAY_EMOJI_ID = "4969785943297884856"

WELCOME_WAVE_EMOJI_ID = "5472055112702629499"
WELCOME_SMILE_EMOJI_ID = "5370738629486319646"
WELCOME_SALAD_EMOJI_ID = "5264946326491134516"
WELCOME_MUSCLE_EMOJI_ID = "5471883477219549006"
BACK_EMOJI_ID = "5255703720078879038"
STATISTICS_EMOJI_ID = "5190806721286657692"
BROADCAST_EMOJI_ID = "5370599459661045441"
BROADCAST_START_EMOJI_ID = "5445284980978621387"
ERROR_EMOJI_ID = "5852812849780362931"
BLOCKED_EMOJI_ID = "5424857974784925603"
ADMIN_PANEL_EMOJI_ID = "5190498849440931467"
PRIVATE_CHAT_EMOJI_ID = "5231302159739395058"


def custom_emoji(emoji_id: str, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


CHECK_EMOJI_ID = "5852871561983299073"


def check_emoji() -> str:
    return custom_emoji(CHECK_EMOJI_ID, "✅")


def globe_emoji() -> str:
    return custom_emoji(CHANGE_LANG_EMOJI_ID, "🌐")


def flag_emoji(lang: Lang) -> str:
    return custom_emoji(FLAG_EMOJI_IDS[lang], FALLBACK_FLAG[lang])


def point_down() -> str:
    return custom_emoji(POINT_DOWN_EMOJI_ID, "👇")


def play_emoji() -> str:
    return custom_emoji(PLAY_EMOJI_ID, "▶️")


def welcome_emojis() -> dict[str, str]:
    return {
        "wave": custom_emoji(WELCOME_WAVE_EMOJI_ID, "👋"),
        "smile": custom_emoji(WELCOME_SMILE_EMOJI_ID, "😊"),
        "salad": custom_emoji(WELCOME_SALAD_EMOJI_ID, "🥗"),
        "muscle": custom_emoji(WELCOME_MUSCLE_EMOJI_ID, "💪"),
        "point": custom_emoji(POINT_DOWN_EMOJI_ID, "👇"),
    }
