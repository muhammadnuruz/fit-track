from __future__ import annotations

from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.formulas import NutritionPlan, build_nutrition_plan, navy_body_fat
from app.models.enums import ActivityLevel, Gender, Goal
from app.models.measurement import Measurement
from app.models.user import User
from app.models.user_settings import UserSettings


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def user_exists(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def delete_user_completely(session: AsyncSession, telegram_id: int) -> bool:
    """Foydalanuvchini bazadan butunlay o'chiradi: users (measurements/food_logs
    DB cascade orqali) + user_settings. Biror narsa o'chirilsa True qaytaradi."""
    user_res = await session.execute(delete(User).where(User.telegram_id == telegram_id))
    settings_res = await session.execute(
        delete(UserSettings).where(UserSettings.telegram_id == telegram_id)
    )
    await session.commit()
    return bool(user_res.rowcount) or bool(settings_res.rowcount)


async def get_existing_plan(
    session: AsyncSession, telegram_id: int
) -> tuple[User, NutritionPlan, float | None] | None:
    """Ro'yxatdan o'tgan foydalanuvchining rejasini saqlangan ma'lumot +
    oxirgi o'lchovdan qayta hisoblaydi. Vazn topilmasa None qaytaradi."""
    user = await get_by_telegram_id(session, telegram_id)
    if user is None:
        return None
    stmt = (
        select(Measurement)
        .where(Measurement.user_id == user.id)
        .order_by(Measurement.date.desc(), Measurement.id.desc())
        .limit(1)
    )
    measurement = (await session.execute(stmt)).scalar_one_or_none()
    if measurement is None or measurement.weight_kg is None:
        return None
    plan = build_nutrition_plan(
        weight_kg=float(measurement.weight_kg),
        height_cm=float(user.height_cm),
        age=user.age,
        gender=user.gender,
        activity=user.activity_level,
        goal=user.goal,
    )
    body_fat_pct = (
        float(measurement.body_fat_pct) if measurement.body_fat_pct is not None else None
    )
    return user, plan, body_fat_pct


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


async def update_from_onboarding(
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
    """Mavjud foydalanuvchi rejasini qayta hisoblaydi: user maydonlari
    yangilanadi va yangi o'lchov qo'shiladi. User topilmasa — yaratadi."""
    user = await get_by_telegram_id(session, telegram_id)
    if user is None:
        return await create_from_onboarding(
            session,
            telegram_id,
            name=name,
            gender=gender,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity=activity,
            goal=goal,
            waist_cm=waist_cm,
            neck_cm=neck_cm,
            hip_cm=hip_cm,
        )

    plan = build_nutrition_plan(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        activity=activity,
        goal=goal,
    )
    body_fat_pct = _body_fat(gender, height_cm, neck_cm, waist_cm, hip_cm)

    user.name = name
    user.gender = gender
    user.age = age
    user.height_cm = height_cm
    user.activity_level = activity
    user.goal = goal
    user.tdee = plan.tdee
    user.target_kcal = plan.target_kcal
    user.target_protein = plan.macros.protein_g
    user.target_carb = plan.macros.carb_g
    user.target_fat = plan.macros.fat_g

    session.add(
        Measurement(
            user_id=user.id,
            date=date.today(),
            weight_kg=weight_kg,
            waist_cm=waist_cm,
            neck_cm=neck_cm,
            hip_cm=hip_cm,
            body_fat_pct=body_fat_pct,
        )
    )
    await session.flush()

    return user, plan, body_fat_pct
