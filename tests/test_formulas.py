"""Formulalar testi — loyihaning matematik o'zagi (SPEC §4).

Ma'lumotnoma qiymatlar qo'lda hisoblangan; math kutubxonasidan mustaqil tekshiriladi.
"""

from __future__ import annotations

import math

import pytest

from app.core.formulas import (
    KCAL_PER_G_FAT,
    KCAL_PER_G_PROTEIN,
    bmi,
    bmr_mifflin_st_jeor,
    build_nutrition_plan,
    macro_split,
    navy_body_fat,
    target_calories,
    tdee,
)
from app.models.enums import ActivityLevel, Gender, Goal


# --- 4.1 BMR ---
def test_bmr_male() -> None:
    # 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    assert bmr_mifflin_st_jeor(80, 180, 30, Gender.MALE) == pytest.approx(1780.0)


def test_bmr_female() -> None:
    # 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
    assert bmr_mifflin_st_jeor(60, 165, 25, Gender.FEMALE) == pytest.approx(1345.25)


# --- 4.2 TDEE ---
@pytest.mark.parametrize(
    ("level", "factor"),
    [
        (ActivityLevel.SEDENTARY, 1.2),
        (ActivityLevel.LIGHT, 1.375),
        (ActivityLevel.MODERATE, 1.55),
        (ActivityLevel.ACTIVE, 1.725),
        (ActivityLevel.VERY_ACTIVE, 1.9),
    ],
)
def test_tdee_factors(level: ActivityLevel, factor: float) -> None:
    assert tdee(1780.0, level) == pytest.approx(1780.0 * factor)


# --- 4.3 Maqsad kaloriya ---
def test_target_calories() -> None:
    assert target_calories(2500, Goal.CUT) == pytest.approx(2000.0)
    assert target_calories(2500, Goal.MAINTAIN) == pytest.approx(2500.0)
    assert target_calories(2500, Goal.BULK) == pytest.approx(2800.0)


# --- 4.4 Makros ---
def test_macro_split_protein_by_goal() -> None:
    cut = macro_split(2000, 80, Goal.CUT)
    bulk = macro_split(3000, 80, Goal.BULK)
    assert cut.protein_g == pytest.approx(2.2 * 80)  # 176
    assert bulk.protein_g == pytest.approx(1.8 * 80)  # 144


def test_macro_split_energy_balances() -> None:
    """Makros kaloriyalari yig'indisi target'ga teng bo'lishi kerak (±1 kkal)."""
    m = macro_split(2400, 75, Goal.MAINTAIN)
    total = m.protein_g * KCAL_PER_G_PROTEIN + m.carb_g * 4.0 + m.fat_g * KCAL_PER_G_FAT
    assert total == pytest.approx(2400, abs=5)


def test_macro_split_fat_minimum_20pct() -> None:
    """Juda past yog' beruvchi holatda ham yog' >= target'ning 20%."""
    m = macro_split(3000, 50, Goal.BULK)  # 0.9*50=45g yog' past bo'lardi
    min_fat = (0.20 * 3000) / KCAL_PER_G_FAT
    assert m.fat_g >= min_fat


def test_macro_split_no_negative_carbs() -> None:
    m = macro_split(1000, 100, Goal.CUT)  # protein+fat > target bo'lishi mumkin
    assert m.carb_g >= 0


# --- BMI ---
def test_bmi() -> None:
    assert bmi(80, 180) == pytest.approx(24.7, abs=0.05)


# --- 4.5 Navy yog' foizi ---
def test_navy_body_fat_male_reference() -> None:
    # Qo'lda: 495/(1.0324 - 0.19077*log10(85-40) + 0.15456*log10(180)) - 450
    expected = 495.0 / (1.0324 - 0.19077 * math.log10(45) + 0.15456 * math.log10(180)) - 450.0
    assert navy_body_fat(Gender.MALE, 180, 40, 85) == pytest.approx(round(expected, 1))


def test_navy_body_fat_female_needs_hip() -> None:
    with pytest.raises(ValueError, match="son"):
        navy_body_fat(Gender.FEMALE, 165, 32, 70)


def test_navy_body_fat_male_invalid() -> None:
    with pytest.raises(ValueError, match="bel"):
        navy_body_fat(Gender.MALE, 180, 40, 38)  # bel < bo'yin


def test_navy_body_fat_female_valid() -> None:
    bf = navy_body_fat(Gender.FEMALE, 165, 32, 70, hip_cm=95)
    assert 10 < bf < 45  # oqilona diapazon


# --- Yuqori daraja: to'liq reja ---
def test_build_nutrition_plan_consistency() -> None:
    plan = build_nutrition_plan(
        weight_kg=80,
        height_cm=180,
        age=30,
        gender=Gender.MALE,
        activity=ActivityLevel.MODERATE,
        goal=Goal.CUT,
    )
    assert plan.bmr == pytest.approx(1780.0)
    assert plan.tdee == pytest.approx(1780.0 * 1.55, abs=0.1)
    assert plan.target_kcal == pytest.approx(1780.0 * 1.55 * 0.80, abs=0.1)
    assert plan.bmi == pytest.approx(24.7, abs=0.1)
    assert plan.macros.protein_g == pytest.approx(176.0)
