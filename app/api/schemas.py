from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import ActivityLevel, Gender, Goal


class OnboardingIn(BaseModel):
    init_data: str
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
