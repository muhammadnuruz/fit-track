from __future__ import annotations

MESSAGES: dict[str, str] = {
    "cmd_start_desc": "Boshlash",
    "cmd_language_desc": "Tilni almashtirish",
    "cmd_help_desc": "Yordam",
    "btn_change_language": "Tilni o'zgartirish",
    "btn_start_onboarding": "Boshlash",
    "btn_open_app": "FitTrack'ni ochish",
    "btn_my_plan": "Kunlik normam",
    "btn_recalc": "Qayta hisoblash",
    "onboarding_cta": "Profilingizni to'ldiring va shaxsiy rejangizni oling {point}",
    "plan_ready": (
        "{e_check} <b>{name}</b>, rejangiz tayyor!\n\n"
        "{e_fire} Kunlik kaloriya: <b>{kcal} kkal</b>\n"
        "{e_protein} Protein: <b>{protein} g</b>\n"
        "{e_carb} Uglevod: <b>{carb} g</b>\n"
        "{e_fat} Yog': <b>{fat} g</b>\n\n"
        "{e_stats} BMI: <b>{bmi}</b> · TDEE: <b>{tdee} kkal</b>"
    ),
    "plan_bodyfat": "{e_dna} Tana yog'i: <b>{bf}%</b>",
    "choose_language": "Tilni tanlang:",
    "language_changed": "{check} Til {flag} <b>O'zbekcha</b> ga o'zgartirildi.",
    "start_welcome": (
        "{wave} <b>FitTrack</b>'ga xush kelibsiz! {smile}\n\n"
        "{salad} Sog'lom hayot va maqsadlaringiz sari ishonchli yordamchingiz {muscle}\n\n"
        "Boshlash uchun /help ni bosing {point}"
    ),
    "help_text": (
        "<b>Buyruqlar:</b>\n"
        "/start — boshlash\n"
        "/help — yordam\n\n"
        "{globe} Tilni istalgan payt pastdagi <b>«Tilni o'zgartirish»</b> "
        "knopkasi orqali almashtirasiz.\n\n"
    ),
}
