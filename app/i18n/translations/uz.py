"""O'zbekcha (uz) tarjimalar. Kalit → matn."""

from __future__ import annotations

MESSAGES: dict[str, str] = {
    # --- Buyruqlar menyusi (Telegram command list) ---
    "cmd_start_desc": "Boshlash",
    "cmd_language_desc": "Tilni almashtirish",
    "cmd_help_desc": "Yordam",
    # --- Til tanlash ---
    "btn_change_language": "Tilni o'zgartirish",
    "choose_language": "Tilni tanlang:",
    "language_changed": "{check} Til {flag} <b>O'zbekcha</b> ga o'zgartirildi.",
    # --- Umumiy ---
    "start_welcome": (
        "{wave} <b>FitTrack</b> ga xush kelibsiz! {salad} Men sizga makros (BJU) hisoblab, "
        "tana tarkibingizni o'zgartirishga yordam beraman. {muscle}\n\n"
        "Boshlash uchun /help ni bosing."
    ),
    "help_text": (
        "<b>Buyruqlar:</b>\n"
        "/start — boshlash\n"
        "/help — yordam\n\n"
        "{globe} Tilni istalgan payt pastdagi <b>«Tilni o'zgartirish»</b> "
        "knopkasi orqali almashtirasiz.\n\n"
    ),
}
