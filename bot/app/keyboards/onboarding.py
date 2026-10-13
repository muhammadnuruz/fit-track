from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n import Lang, t

START_CALLBACK = "ob:start"
GENDER_PREFIX = "ob:gender:"
ACTIVITY_PREFIX = "ob:activity:"
GOAL_PREFIX = "ob:goal:"

GENDERS = ("male", "female")
ACTIVITIES = ("sedentary", "light", "moderate", "active", "very_active")
GOALS = ("cut", "maintain", "bulk")


def start_onboarding_keyboard(lang: Lang) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_start_onboarding", lang), callback_data=START_CALLBACK)
    return builder.as_markup()


def _choice_keyboard(
    prefix: str, options: tuple[str, ...], labels: dict[str, str]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.button(text=labels[option], callback_data=f"{prefix}{option}")
    builder.adjust(1)
    return builder.as_markup()


def gender_keyboard(lang: Lang) -> InlineKeyboardMarkup:
    labels = {"male": t("gender_male", lang), "female": t("gender_female", lang)}
    return _choice_keyboard(GENDER_PREFIX, GENDERS, labels)


def activity_keyboard(lang: Lang) -> InlineKeyboardMarkup:
    labels = {option: t(f"activity_{option}", lang) for option in ACTIVITIES}
    return _choice_keyboard(ACTIVITY_PREFIX, ACTIVITIES, labels)


def goal_keyboard(lang: Lang) -> InlineKeyboardMarkup:
    labels = {option: t(f"goal_{option}", lang) for option in GOALS}
    return _choice_keyboard(GOAL_PREFIX, GOALS, labels)
