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


def test_bmr_male() -> None:
    assert bmr_mifflin_st_jeor(80, 180, 30, Gender.MALE) == pytest.approx(1780.0)


def test_bmr_female() -> None:
    assert bmr_mifflin_st_jeor(60, 165, 25, Gender.FEMALE) == pytest.approx(1345.25)


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


def test_target_calories() -> None:
    assert target_calories(2500, Goal.CUT) == pytest.approx(2000.0)
    assert target_calories(2500, Goal.MAINTAIN) == pytest.approx(2500.0)
    assert target_calories(2500, Goal.BULK) == pytest.approx(2800.0)


def test_macro_split_protein_by_goal() -> None:
    cut = macro_split(2000, 80, Goal.CUT)
    bulk = macro_split(3000, 80, Goal.BULK)
    assert cut.protein_g == pytest.approx(2.2 * 80)
    assert bulk.protein_g == pytest.approx(1.8 * 80)


def test_macro_split_energy_balances() -> None:
    m = macro_split(2400, 75, Goal.MAINTAIN)
    total = m.protein_g * KCAL_PER_G_PROTEIN + m.carb_g * 4.0 + m.fat_g * KCAL_PER_G_FAT
    assert total == pytest.approx(2400, abs=5)


def test_macro_split_fat_minimum_20pct() -> None:
    m = macro_split(3000, 50, Goal.BULK)
    min_fat = (0.20 * 3000) / KCAL_PER_G_FAT
    assert m.fat_g >= min_fat


def test_macro_split_no_negative_carbs() -> None:
    m = macro_split(1000, 100, Goal.CUT)
    assert m.carb_g >= 0


def test_bmi() -> None:
    assert bmi(80, 180) == pytest.approx(24.7, abs=0.05)


def test_navy_body_fat_male_reference() -> None:
    expected = 495.0 / (1.0324 - 0.19077 * math.log10(45) + 0.15456 * math.log10(180)) - 450.0
    assert navy_body_fat(Gender.MALE, 180, 40, 85) == pytest.approx(round(expected, 1))


def test_navy_body_fat_female_needs_hip() -> None:
    with pytest.raises(ValueError, match="son"):
        navy_body_fat(Gender.FEMALE, 165, 32, 70)


def test_navy_body_fat_male_invalid() -> None:
    with pytest.raises(ValueError, match="bel"):
        navy_body_fat(Gender.MALE, 180, 40, 38)


def test_navy_body_fat_female_valid() -> None:
    bf = navy_body_fat(Gender.FEMALE, 165, 32, 70, hip_cm=95)
    assert 10 < bf < 45


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
