from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.formulas import NutritionPlan, build_nutrition_plan, navy_body_fat
from app.models.enums import ActivityLevel, Gender, Goal
from app.models.measurement import Measurement
from app.models.user import User


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def user_exists(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


def _body_fat(
    gender: Gender,
    height_cm: float,
    neck_cm: float | None,
    waist_cm: float | None,
    hip_cm: float | None,
) -> float | None:
    if neck_cm is None or waist_cm is None:
        return None
    if gender is Gender.FEMALE and hip_cm is None:
        return None
    try:
        return navy_body_fat(
            gender=gender,
            height_cm=height_cm,
            neck_cm=neck_cm,
            waist_cm=waist_cm,
            hip_cm=hip_cm,
        )
    except ValueError:
        return None


async def create_from_onboarding(
    session: AsyncSession,
    telegram_id: int,
    *,
    name: str,
    gender: Gender,
    age: int,
    height_cm: float,
    weight_kg: float,
    activity: ActivityLevel,
    goal: Goal,
    waist_cm: float | None,
    neck_cm: float | None,
    hip_cm: float | None,
) -> tuple[User, NutritionPlan, float | None]:
    plan = build_nutrition_plan(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        activity=activity,
        goal=goal,
    )
    body_fat_pct = _body_fat(gender, height_cm, neck_cm, waist_cm, hip_cm)

    user = User(
        telegram_id=telegram_id,
        name=name,
        gender=gender,
        age=age,
        height_cm=height_cm,
        activity_level=activity,
        goal=goal,
        tdee=plan.tdee,
        target_kcal=plan.target_kcal,
        target_protein=plan.macros.protein_g,
        target_carb=plan.macros.carb_g,
        target_fat=plan.macros.fat_g,
    )
    session.add(user)
    await session.flush()

    measurement = Measurement(
        user_id=user.id,
        date=date.today(),
        weight_kg=weight_kg,
        waist_cm=waist_cm,
        neck_cm=neck_cm,
        hip_cm=hip_cm,
        body_fat_pct=body_fat_pct,
    )
    session.add(measurement)
    await session.flush()

    return user, plan, body_fat_pct
