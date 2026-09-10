from __future__ import annotations

from app.bot.emoji import bodyfat_emoji, plan_emojis
from app.core.formulas import NutritionPlan
from app.i18n import Lang, t


def build_plan_text(
    lang: Lang,
    plan: NutritionPlan,
    body_fat_pct: float | None,
    name: str,
    *,
    plain: bool = False,
) -> str:
    """Reja xabari matnini yasaydi (premium emoji bilan; plain=True bo'lsa oddiy)."""
    text = t(
        "plan_ready",
        lang,
        name=name,
        kcal=plan.target_kcal,
        protein=plan.macros.protein_g,
        carb=plan.macros.carb_g,
        fat=plan.macros.fat_g,
        bmi=plan.bmi,
        tdee=plan.tdee,
        **plan_emojis(plain=plain),
    )
    if body_fat_pct is not None:
        text = f"{text}\n{t('plan_bodyfat', lang, bf=body_fat_pct, e_dna=bodyfat_emoji(plain=plain))}"
    return text
