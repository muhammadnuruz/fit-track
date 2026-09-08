"""English (en) translations. Key → text."""

from __future__ import annotations

MESSAGES: dict[str, str] = {
    # --- Commands menu ---
    "cmd_start_desc": "Start",
    "cmd_language_desc": "Change language",
    "cmd_help_desc": "Help",
    # --- Language selection ---
    "choose_language": "🌐 Choose your language:",
    "language_changed": "✅ Language changed to <b>English</b>.",
    # --- Common ---
    "start_welcome": (
        "👋 Welcome to <b>FitTrack</b>!\n\n"
        "I'll help you track macros and reshape your body composition — "
        "and I know local dishes too.\n\n"
        "Tap /help to get started.\n"
        "<i>(Onboarding flow lands in the next stage.)</i>"
    ),
    "help_text": (
        "<b>Commands:</b>\n"
        "/start — start\n"
        "/language — change language\n"
        "/help — help\n\n"
        "Coming soon: profile setup, food logging, weekly check-in."
    ),
}
