from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    name = State()
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()


class AdminBroadcast(StatesGroup):
    waiting_message = State()


class AdminDeleteUser(StatesGroup):
    waiting_user_id = State()
