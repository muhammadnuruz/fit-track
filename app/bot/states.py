from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    name = State()
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()
    waist = State()
    neck = State()
    hip = State()


class CheckIn(StatesGroup):
    weight = State()
    waist = State()
    neck = State()
    hip = State()
    mood = State()
    photo = State()


class AdminBroadcast(StatesGroup):
    waiting_message = State()
