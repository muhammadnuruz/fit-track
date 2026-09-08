"""O'zbekcha (uz) tarjimalar. Kalit → matn."""

from __future__ import annotations

MESSAGES: dict[str, str] = {
    # --- Buyruqlar menyusi (Telegram command list) ---
    "cmd_start_desc": "Boshlash",
    "cmd_language_desc": "Tilni almashtirish",
    "cmd_help_desc": "Yordam",
    # --- Til tanlash ---
    "choose_language": "🌐 Tilni tanlang:",
    "language_changed": "✅ Til <b>O'zbekcha</b> ga o'zgartirildi.",
    # --- Umumiy ---
    "start_welcome": (
        "👋 <b>FitTrack</b> ga xush kelibsiz!\n\n"
        "Men sizga makros (BJU) hisoblab, tana tarkibingizni o'zgartirishga "
        "yordam beraman — mahalliy taomlarni ham bilaman.\n\n"
        "Boshlash uchun /help ni bosing.\n"
        "<i>(Onboarding oqimi keyingi bosqichda ulanadi.)</i>"
    ),
    "help_text": (
        "<b>Buyruqlar:</b>\n"
        "/start — boshlash\n"
        "/language — tilni almashtirish\n"
        "/help — yordam\n\n"
        "Tez orada: profil sozlash, ovqat loglash, haftalik check-in."
    ),
}
