from __future__ import annotations

import math
from dataclasses import dataclass

from app.models.enums import ActivityLevel, Gender, Goal

ACTIVITY_FACTORS: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

GOAL_FACTORS: dict[Goal, float] = {
    Goal.CUT: 0.80,
    Goal.MAINTAIN: 1.00,
    Goal.BULK: 1.12,
}

KCAL_PER_G_PROTEIN = 4.0
KCAL_PER_G_CARB = 4.0
KCAL_PER_G_FAT = 9.0


@dataclass(frozen=True, slots=True)
class Macros:
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float


@dataclass(frozen=True, slots=True)
class NutritionPlan:
    bmr: float
    tdee: float
    target_kcal: float
    macros: Macros
    bmi: float


def bmr_mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, gender: Gender) -> float:
    base = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age
    return base + 5.0 if gender is Gender.MALE else base - 161.0


def tdee(bmr: float, activity: ActivityLevel) -> float:
    return bmr * ACTIVITY_FACTORS[activity]


def target_calories(tdee_value: float, goal: Goal) -> float:
    return tdee_value * GOAL_FACTORS[goal]


def macro_split(target_kcal: float, weight_kg: float, goal: Goal) -> Macros:
    protein_per_kg = {Goal.CUT: 2.2, Goal.MAINTAIN: 2.0, Goal.BULK: 1.8}[goal]
    protein_g = protein_per_kg * weight_kg

    fat_g = 0.9 * weight_kg
    min_fat_g = (0.20 * target_kcal) / KCAL_PER_G_FAT
    fat_g = max(fat_g, min_fat_g)

    protein_kcal = protein_g * KCAL_PER_G_PROTEIN
    fat_kcal = fat_g * KCAL_PER_G_FAT
    remaining_kcal = target_kcal - protein_kcal - fat_kcal
    carb_g = max(remaining_kcal, 0.0) / KCAL_PER_G_CARB

    return Macros(
        kcal=round(target_kcal, 1),
        protein_g=round(protein_g, 1),
        carb_g=round(carb_g, 1),
        fat_g=round(fat_g, 1),
    )


def bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m * height_m), 1)


def navy_body_fat(
    gender: Gender,
    height_cm: float,
    neck_cm: float,
    waist_cm: float,
    hip_cm: float | None = None,
) -> float:
    if gender is Gender.MALE:
        diff = waist_cm - neck_cm
        if diff <= 0:
            raise ValueError("bel bo'yindan katta bo'lishi kerak (erkak)")
        denom = 1.0324 - 0.19077 * math.log10(diff) + 0.15456 * math.log10(height_cm)
    else:
        if hip_cm is None:
            raise ValueError("ayollar uchun son (hip_cm) o'lchovi zarur")
        total = waist_cm + hip_cm - neck_cm
        if total <= 0:
            raise ValueError("bel + son bo'yindan katta bo'lishi kerak (ayol)")
        denom = 1.29579 - 0.35004 * math.log10(total) + 0.22100 * math.log10(height_cm)

    bf = 495.0 / denom - 450.0
    return round(bf, 1)


def build_nutrition_plan(
    *,
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender,
    activity: ActivityLevel,
    goal: Goal,
) -> NutritionPlan:
    bmr_value = bmr_mifflin_st_jeor(weight_kg, height_cm, age, gender)
    tdee_value = tdee(bmr_value, activity)
    target = target_calories(tdee_value, goal)
    macros = macro_split(target, weight_kg, goal)
    return NutritionPlan(
        bmr=round(bmr_value, 1),
        tdee=round(tdee_value, 1),
        target_kcal=round(target, 1),
        macros=macros,
        bmi=bmi(weight_kg, height_cm),
    )
