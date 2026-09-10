from __future__ import annotations

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
    waist_cm: float | None = Field(default=None, ge=30, le=250)
    neck_cm: float | None = Field(default=None, ge=15, le=100)
    hip_cm: float | None = Field(default=None, ge=40, le=250)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name is required")
        if len(cleaned) < 2:
            raise ValueError("name must be at least 2 characters long")
        if not _NAME_PATTERN.fullmatch(cleaned):
            raise ValueError("name contains unsupported characters")
        return cleaned

    @field_validator("height_cm", "weight_kg", "waist_cm", "neck_cm", "hip_cm")
    @classmethod
    def validate_positive_measurements(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("measurement must be positive")
        return value


class OnboardingIn(ProfileIn):
    init_data: str


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
    body_fat_pct: float | None = None
    macros: MacrosOut


class OnboardingOut(BaseModel):
    ok: bool
    already: bool
    plan: PlanOut | None = None


class MeProfileOut(BaseModel):
    name: str
    gender: Gender
    age: int
    height_cm: float
    weight_kg: float | None = None
    activity: ActivityLevel
    goal: Goal
    waist_cm: float | None = None
    neck_cm: float | None = None
    hip_cm: float | None = None
    avatar_url: str | None = None


class MeOut(BaseModel):
    registered: bool
    profile: MeProfileOut | None = None
    plan: PlanOut | None = None
