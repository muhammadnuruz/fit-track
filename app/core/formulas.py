"""Loyihaning matematik o'zagi — SPEC §4.

Barcha formulalar sof (pure) funksiyalar: kirish → chiqish, yon ta'sirsiz.
Shu sabab to'liq test qilinadi (`tests/test_formulas.py`).

Birliklar: vazn kg, bo'y/o'lchovlar sm, yosh yil.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.models.enums import ActivityLevel, Gender, Goal

# --- SPEC §4.2: faollik koeffitsientlari ---
ACTIVITY_FACTORS: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

# --- SPEC §4.3: maqsadga ko'ra kaloriya koeffitsienti ---
GOAL_FACTORS: dict[Goal, float] = {
    Goal.CUT: 0.80,  # −20%
    Goal.MAINTAIN: 1.00,
    Goal.BULK: 1.12,  # +12%
}

# Kaloriya koeffitsientlari (Atwater): 1g protein/uglevod = 4 kkal, yog' = 9 kkal.
KCAL_PER_G_PROTEIN = 4.0
KCAL_PER_G_CARB = 4.0
KCAL_PER_G_FAT = 9.0


@dataclass(frozen=True, slots=True)
class Macros:
    """Kunlik makros taqsimoti (gramm) va kaloriya."""

    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float


@dataclass(frozen=True, slots=True)
class NutritionPlan:
    """Onboarding natijasi — foydalanuvchiga darrov ko'rsatiladigan qiymatlar."""

    bmr: float
    tdee: float
    target_kcal: float
    macros: Macros
    bmi: float


# ---------------------------------------------------------------------------
# 4.1 BMR — Mifflin-St Jeor
# ---------------------------------------------------------------------------
def bmr_mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, gender: Gender) -> float:
    """Asosiy metabolizm (BMR).

    Erkak:  10·vazn + 6.25·bo'y − 5·yosh + 5
    Ayol:   10·vazn + 6.25·bo'y − 5·yosh − 161
    """
    base = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age
    return base + 5.0 if gender is Gender.MALE else base - 161.0


# ---------------------------------------------------------------------------
# 4.2 TDEE
# ---------------------------------------------------------------------------
def tdee(bmr: float, activity: ActivityLevel) -> float:
    """Kunlik umumiy energiya sarfi = BMR × faollik faktori."""
    return bmr * ACTIVITY_FACTORS[activity]


# ---------------------------------------------------------------------------
# 4.3 Maqsadga ko'ra kaloriya
# ---------------------------------------------------------------------------
def target_calories(tdee_value: float, goal: Goal) -> float:
    """Maqsad (cut/maintain/bulk) bo'yicha kunlik kaloriya normasi."""
    return tdee_value * GOAL_FACTORS[goal]


# ---------------------------------------------------------------------------
# 4.4 Makros taqsimoti
# ---------------------------------------------------------------------------
def macro_split(target_kcal: float, weight_kg: float, goal: Goal) -> Macros:
    """Kunlik makroslarni gramm hisobida taqsimlash (SPEC §4.4).

    Protein: 1.8–2.2 g/kg (cut'da yuqori chetiga yaqin).
    Yog':    0.8–1.0 g/kg, ammo kamida umumiy kaloriyaning 20%.
    Uglevod: qolgan kaloriyalardan.
    """
    # Protein: cut'da yuqori (2.2), bulk'da past (1.8), maintain o'rtada (2.0).
    protein_per_kg = {Goal.CUT: 2.2, Goal.MAINTAIN: 2.0, Goal.BULK: 1.8}[goal]
    protein_g = protein_per_kg * weight_kg

    # Yog': 0.9 g/kg bazaviy, lekin kamida target'ning 20% i.
    fat_g = 0.9 * weight_kg
    min_fat_g = (0.20 * target_kcal) / KCAL_PER_G_FAT
    fat_g = max(fat_g, min_fat_g)

    # Uglevod: qolgan kaloriyalardan.
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


# ---------------------------------------------------------------------------
# BMI (yordamchi ko'rsatkich)
# ---------------------------------------------------------------------------
def bmi(weight_kg: float, height_cm: float) -> float:
    """Tana massasi indeksi = vazn / bo'y(m)²."""
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m * height_m), 1)


# ---------------------------------------------------------------------------
# 4.5 Yog' foizi — U.S. Navy metodi
# ---------------------------------------------------------------------------
def navy_body_fat(
    gender: Gender,
    height_cm: float,
    neck_cm: float,
    waist_cm: float,
    hip_cm: float | None = None,
) -> float:
    """U.S. Navy yog' foizi (%). O'lchovlar sm da, log10 asosida.

    Erkak: 495 / (1.0324 − 0.19077·log10(bel − bo'yin) + 0.15456·log10(bo'y)) − 450
    Ayol:  495 / (1.29579 − 0.35004·log10(bel + son − bo'yin) + 0.22100·log10(bo'y)) − 450

    Eslatma: bu TAXMIN, klinik o'lchov emas (SPEC §9).
    """
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


# ---------------------------------------------------------------------------
# Yuqori darajali yordamchi — onboarding to'liq rejasi
# ---------------------------------------------------------------------------
def build_nutrition_plan(
    *,
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender,
    activity: ActivityLevel,
    goal: Goal,
) -> NutritionPlan:
    """Onboarding: BMR → TDEE → target → makros + BMI ni bir joyda hisoblaydi."""
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
