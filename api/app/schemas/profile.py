import re

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ActivityLevel, Gender, Goal

_NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё'\- ]+$")


class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    gender: Gender
    age: int = Field(ge=10, le=100)
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=30, le=350)
    activity: ActivityLevel
    goal: Goal

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("name must be at least 2 characters long")
        if not _NAME_PATTERN.fullmatch(cleaned):
            raise ValueError("name contains unsupported characters")
        return cleaned


class MacrosOut(BaseModel):
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float


class PlanOut(BaseModel):
    bmr: float
    tdee: float
    target_kcal: float
    bmi: float
    macros: MacrosOut


class ProfileOut(BaseModel):
    name: str
    gender: Gender
    age: int
    height_cm: float
    weight_kg: float | None
    activity: ActivityLevel
    goal: Goal
    plan: PlanOut | None
