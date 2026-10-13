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


class Language(str, enum.Enum):
    UZ = "uz"
    RU = "ru"
    EN = "en"
