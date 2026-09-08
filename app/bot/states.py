"""FSM holatlari — onboarding va check-in oqimlari (Bosqich 0/2 da to'ldiriladi)."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    """SPEC §2.1 — ketma-ket profil so'rovi."""

    name = State()
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()
    # Ixtiyoriy boshlang'ich o'lchovlar:
    waist = State()
    neck = State()
    hip = State()


class CheckIn(StatesGroup):
    """SPEC §2.3 — haftalik check-in."""

    weight = State()
    waist = State()
    neck = State()
    hip = State()
    mood = State()
    photo = State()
