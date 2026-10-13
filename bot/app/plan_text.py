from app.api_client import Profile
from app.i18n import Lang, t


def build_plan_text(lang: Lang, profile: Profile) -> str:
    if profile.plan is None:
        return t("plan_no_profile", lang)
    plan = profile.plan
    return t(
        "plan_ready",
        lang,
        name=profile.name,
        kcal=plan.target_kcal,
        protein=plan.macros.protein_g,
        carb=plan.macros.carb_g,
        fat=plan.macros.fat_g,
        bmi=plan.bmi,
        tdee=plan.tdee,
    )
