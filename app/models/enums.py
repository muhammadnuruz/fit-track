from __future__ import annotations

import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Goal(str, enum.Enum):
    CUT = "cut"
    MAINTAIN = "maintain"
    BULK = "bulk"


class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class FoodSource(str, enum.Enum):
    OPEN_DB = "open_db"
    MANUAL = "manual"
    USER = "user"
