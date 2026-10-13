import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api_client import ApiClient, ApiError, ProfileInput
from app.i18n import DEFAULT_LANG, Lang, t
from app.keyboards.onboarding import (
    ACTIVITY_PREFIX,
    GENDER_PREFIX,
    GOAL_PREFIX,
    START_CALLBACK,
    activity_keyboard,
    gender_keyboard,
    goal_keyboard,
)
from app.plan_text import build_plan_text
from app.states import Onboarding
from app.validation import parse_age, parse_name, parse_number

router = Router(name="onboarding")
log = logging.getLogger(__name__)


@router.callback_query(F.data == START_CALLBACK)
async def on_start_onboarding(
    callback: CallbackQuery, state: FSMContext, lang: Lang | None
) -> None:
    await callback.answer()
    if isinstance(callback.message, Message):
        await _begin(callback.message, state, lang or DEFAULT_LANG)


async def _begin(message: Message, state: FSMContext, lang: Lang) -> None:
    await state.clear()
    await state.set_state(Onboarding.name)
    await message.answer(t("onboarding_ask_name", lang))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, lang: Lang | None) -> None:
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer(t("onboarding_cancelled", lang or DEFAULT_LANG))


@router.message(Onboarding.name, F.text, ~F.text.startswith("/"))
async def on_name(message: Message, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    name = parse_name(message.text or "")
    if name is None:
        await message.answer(t("onboarding_invalid_name", effective))
        return
    await state.update_data(name=name)
    await state.set_state(Onboarding.gender)
    await message.answer(
        t("onboarding_ask_gender", effective), reply_markup=gender_keyboard(effective)
    )


@router.callback_query(Onboarding.gender, F.data.startswith(GENDER_PREFIX))
async def on_gender(callback: CallbackQuery, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    assert callback.data is not None
    await state.update_data(gender=callback.data.removeprefix(GENDER_PREFIX))
    await state.set_state(Onboarding.age)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(t("onboarding_ask_age", effective))


@router.message(Onboarding.age, F.text, ~F.text.startswith("/"))
async def on_age(message: Message, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    age = parse_age(message.text or "")
    if age is None:
        await message.answer(t("onboarding_invalid_age", effective))
        return
    await state.update_data(age=age)
    await state.set_state(Onboarding.height)
    await message.answer(t("onboarding_ask_height", effective))


@router.message(Onboarding.height, F.text, ~F.text.startswith("/"))
async def on_height(message: Message, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    height = parse_number(message.text or "", 100, 250)
    if height is None:
        await message.answer(t("onboarding_invalid_height", effective))
        return
    await state.update_data(height_cm=height)
    await state.set_state(Onboarding.weight)
    await message.answer(t("onboarding_ask_weight", effective))


@router.message(Onboarding.weight, F.text, ~F.text.startswith("/"))
async def on_weight(message: Message, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    weight = parse_number(message.text or "", 30, 350)
    if weight is None:
        await message.answer(t("onboarding_invalid_weight", effective))
        return
    await state.update_data(weight_kg=weight)
    await state.set_state(Onboarding.activity)
    await message.answer(
        t("onboarding_ask_activity", effective), reply_markup=activity_keyboard(effective)
    )


@router.callback_query(Onboarding.activity, F.data.startswith(ACTIVITY_PREFIX))
async def on_activity(callback: CallbackQuery, state: FSMContext, lang: Lang | None) -> None:
    effective = lang or DEFAULT_LANG
    assert callback.data is not None
    await state.update_data(activity=callback.data.removeprefix(ACTIVITY_PREFIX))
    await state.set_state(Onboarding.goal)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(
            t("onboarding_ask_goal", effective), reply_markup=goal_keyboard(effective)
        )


@router.callback_query(Onboarding.goal, F.data.startswith(GOAL_PREFIX))
async def on_goal(
    callback: CallbackQuery, state: FSMContext, lang: Lang | None, api: ApiClient
) -> None:
    effective = lang or DEFAULT_LANG
    assert callback.data is not None
    await state.update_data(goal=callback.data.removeprefix(GOAL_PREFIX))
    data = await state.get_data()
    profile_input = ProfileInput(
        name=data["name"],
        gender=data["gender"],
        age=data["age"],
        height_cm=data["height_cm"],
        weight_kg=data["weight_kg"],
        activity=data["activity"],
        goal=data["goal"],
    )
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    try:
        profile = await api.upsert_profile(callback.from_user.id, profile_input)
    except ApiError:
        log.warning("profile save failed for %s", callback.from_user.id)
        await callback.message.answer(t("service_unavailable", effective))
        return
    await state.clear()
    await callback.message.answer(build_plan_text(effective, profile))
