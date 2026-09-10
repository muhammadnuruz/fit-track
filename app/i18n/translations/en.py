from __future__ import annotations

MESSAGES: dict[str, str] = {
    "cmd_start_desc": "Start",
    "cmd_language_desc": "Change language",
    "cmd_help_desc": "Help",
    "btn_change_language": "Change language",
    "btn_start_onboarding": "▶️ Start",
    "onboarding_cta": "Complete your profile and get your personal plan {point}",
    "plan_ready": (
        "{e_check} <b>{name}</b>, your plan is ready!\n\n"
        "{e_fire} Daily calories: <b>{kcal} kcal</b>\n"
        "{e_protein} Protein: <b>{protein} g</b>\n"
        "{e_carb} Carbs: <b>{carb} g</b>\n"
        "{e_fat} Fat: <b>{fat} g</b>\n\n"
        "{e_stats} BMI: <b>{bmi}</b> · TDEE: <b>{tdee} kcal</b>"
    ),
    "plan_bodyfat": "{e_dna} Body fat: <b>{bf}%</b>",
    "choose_language": "Choose your language:",
    "language_changed": "{check} Language changed to {flag} <b>English</b>.",
    "start_welcome": (
        "{wave} Welcome to <b>FitTrack</b>! {smile}\n\n"
        "{salad} Your reliable companion on the way to a healthy life and your goals {muscle}\n\n"
        "Tap /help to get started {point}"
    ),
    "help_text": (
        "<b>Commands:</b>\n"
        "/start — start\n"
        "/help — help\n\n"
        "{globe} You can switch language anytime with the <b>«Change language»</b> "
        "button below."
    ),
}
