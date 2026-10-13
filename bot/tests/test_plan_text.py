from app.api_client import Macros, Plan, Profile
from app.i18n import Lang
from app.plan_text import build_plan_text


def _profile(plan: Plan | None) -> Profile:
    return Profile(
        name="Ali",
        gender="male",
        age=28,
        height_cm=178.0,
        weight_kg=82.0,
        activity="moderate",
        goal="bulk",
        plan=plan,
    )


def test_plan_text_contains_targets() -> None:
    plan = Plan(
        bmr=1800.0,
        tdee=2790.0,
        target_kcal=3125.0,
        bmi=25.9,
        macros=Macros(kcal=3125.0, protein_g=147.6, carb_g=380.0, fat_g=74.0),
    )
    text = build_plan_text(Lang.EN, _profile(plan))
    assert "Ali" in text
    assert "3125.0 kcal" in text
    assert "147.6 g" in text


def test_missing_plan_asks_to_register() -> None:
    assert "/start" in build_plan_text(Lang.EN, _profile(None))
