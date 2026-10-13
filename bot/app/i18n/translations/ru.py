MESSAGES: dict[str, str] = {
    "cmd_start_desc": "Начать",
    "cmd_plan_desc": "Моя норма дня",
    "cmd_help_desc": "Помощь",
    "btn_change_language": "Изменить язык",
    "btn_start_onboarding": "Заполнить профиль",
    "choose_language": "Выберите язык:",
    "language_changed": "{check} Язык изменён на {flag} <b>Русский</b>.",
    "start_welcome": (
        "{wave} Добро пожаловать в <b>FitTrack</b>! {smile}\n\n"
        "{salad} Ваш надёжный помощник на пути к здоровой жизни и целям {muscle}\n\n"
        "Нажмите /help, чтобы начать {point}"
    ),
    "onboarding_cta": "Заполните профиль и получите персональный план {point}",
    "onboarding_ask_name": "Введите ваше имя:",
    "onboarding_invalid_name": "Имя должно быть от 2 букв и содержать только буквы.",
    "onboarding_ask_gender": "Выберите пол:",
    "gender_male": "Мужской",
    "gender_female": "Женский",
    "onboarding_ask_age": "Сколько вам лет?",
    "onboarding_invalid_age": "Введите возраст числом от 10 до 100.",
    "onboarding_ask_height": "Какой у вас рост, см?",
    "onboarding_invalid_height": "Введите рост числом от 100 до 250 см.",
    "onboarding_ask_weight": "Какой у вас вес, кг?",
    "onboarding_invalid_weight": "Введите вес числом от 30 до 350 кг.",
    "onboarding_ask_activity": "Выберите уровень активности:",
    "activity_sedentary": "Сидячий образ жизни",
    "activity_light": "Лёгкая (1–3 дня в неделю)",
    "activity_moderate": "Средняя (3–5 дней в неделю)",
    "activity_active": "Высокая (6–7 дней в неделю)",
    "activity_very_active": "Очень высокая (тренировки два раза в день)",
    "onboarding_ask_goal": "Выберите цель:",
    "goal_cut": "Снижение веса",
    "goal_maintain": "Поддержание веса",
    "goal_bulk": "Набор массы",
    "onboarding_saving": "Сохраняем…",
    "onboarding_cancelled": "Отменено. Чтобы начать заново, нажмите /start.",
    "plan_ready": (
        "🎯 <b>{name}</b>, ваш план готов!\n\n"
        "🔥 Калории в день: <b>{kcal} ккал</b>\n"
        "🍖 Белки: <b>{protein} г</b>\n"
        "🍚 Углеводы: <b>{carb} г</b>\n"
        "🥑 Жиры: <b>{fat} г</b>\n\n"
        "📊 ИМТ: <b>{bmi}</b> · TDEE: <b>{tdee} ккал</b>"
    ),
    "plan_no_profile": "Сначала заполните профиль. Нажмите /start.",
    "service_unavailable": "Сервис временно недоступен. Попробуйте чуть позже.",
    "help_text": (
        "<b>Команды:</b>\n"
        "/start — начать\n"
        "/plan — моя норма дня\n"
        "/cancel — отменить заполнение профиля\n"
        "/help — помощь\n\n"
        "{globe} Язык можно сменить в любой момент кнопкой <b>«Изменить язык»</b> внизу."
    ),
}
