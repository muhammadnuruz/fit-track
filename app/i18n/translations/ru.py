from __future__ import annotations

MESSAGES: dict[str, str] = {
    "cmd_start_desc": "Начать",
    "cmd_language_desc": "Сменить язык",
    "cmd_help_desc": "Помощь",
    "btn_change_language": "Изменить язык",
    "btn_start_onboarding": "▶️ Начать",
    "onboarding_cta": "Заполните профиль и получите персональный план {point}",
    "plan_ready": (
        "{e_check} <b>{name}</b>, ваш план готов!\n\n"
        "{e_fire} Калории в день: <b>{kcal} ккал</b>\n"
        "{e_protein} Белки: <b>{protein} г</b>\n"
        "{e_carb} Углеводы: <b>{carb} г</b>\n"
        "{e_fat} Жиры: <b>{fat} г</b>\n\n"
        "{e_stats} ИМТ: <b>{bmi}</b> · TDEE: <b>{tdee} ккал</b>"
    ),
    "plan_bodyfat": "{e_dna} Жир в организме: <b>{bf}%</b>",
    "choose_language": "Выберите язык:",
    "language_changed": "{check} Язык изменён на {flag} <b>Русский</b>.",
    "start_welcome": (
        "{wave} Добро пожаловать в <b>FitTrack</b>! {smile}\n\n"
        "{salad} Ваш надёжный помощник на пути к здоровой жизни и целям {muscle}\n\n"
        "Нажмите /help, чтобы начать {point}"
    ),
    "help_text": (
        "<b>Команды:</b>\n"
        "/start — начать\n"
        "/help — помощь\n\n"
        "{globe} Язык можно сменить в любой момент кнопкой <b>«Изменить язык»</b> внизу."
    ),
}
