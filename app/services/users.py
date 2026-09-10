from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.formulas import NutritionPlan, build_nutrition_plan
from app.models.enums import ActivityLevel, Gender, Goal
from app.models.measurement import Measurement
from app.models.user import User
from app.models.user_settings import UserSettings


def today_local() -> date:
    """settings.tz mintaqasidagi bugungi sana (UTC emas)."""
    return datetime.now(ZoneInfo(settings.tz)).date()


async def _upsert_measurement(
    session: AsyncSession,
    user_id: int,
    *,
    weight_kg: float,
) -> None:
    """Bir kunga bitta o'lchov: bugungi o'lchov bo'lsa yangilaydi, bo'lmasa qo'shadi.
    Bu bir kunда bir necha marta recalculate qilinganda qatorlar cheksiz o'sishini oldini oladi."""
    day = today_local()
    existing = (
        await session.execute(
            select(Measurement).where(
                Measurement.user_id == user_id, Measurement.date == day
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        existing.weight_kg = Decimal(str(weight_kg))
    else:
        session.add(
            Measurement(
                user_id=user_id,
                date=day,
                weight_kg=weight_kg,
            )
        )


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def user_exists(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def delete_user_completely(session: AsyncSession, telegram_id: int) -> bool:
    """Foydalanuvchini bazadan butunlay o'chiradi: users (measurements/food_logs
    DB cascade orqali) + user_settings. Biror narsa o'chirilsa True qaytaradi."""
    user = await get_by_telegram_id(session, telegram_id)
    settings_id = (
        await session.execute(
            select(UserSettings.telegram_id).where(UserSettings.telegram_id == telegram_id)
        )
    ).scalar_one_or_none()
    if user is None and settings_id is None:
        return False
    if user is not None:
        await session.execute(delete(User).where(User.telegram_id == telegram_id))
    if settings_id is not None:
        await session.execute(delete(UserSettings).where(UserSettings.telegram_id == telegram_id))
    await session.commit()
    return True


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


@dataclass(slots=True)
class ProfileData:
    user: User
    weight_kg: float | None
    body_fat_pct: float | None
    plan: NutritionPlan | None


async def load_profile(session: AsyncSession, telegram_id: int) -> ProfileData | None:
    """Dashboard uchun: user + oxirgi o'lchov + (vazn bo'lsa) reja."""
    user = await get_by_telegram_id(session, telegram_id)
    if user is None:
        return None
    stmt = (
        select(Measurement)
        .where(Measurement.user_id == user.id)
        .order_by(Measurement.date.desc(), Measurement.id.desc())
        .limit(1)
    )
    m = (await session.execute(stmt)).scalar_one_or_none()
    weight = float(m.weight_kg) if m is not None and m.weight_kg is not None else None
    plan: NutritionPlan | None = None
    if weight is not None:
        plan = build_nutrition_plan(
            weight_kg=weight,
            height_cm=float(user.height_cm),
            age=user.age,
            gender=user.gender,
            activity=user.activity_level,
            goal=user.goal,
        )
    return ProfileData(
        user=user,
        weight_kg=weight,
        body_fat_pct=(
            float(m.body_fat_pct) if m is not None and m.body_fat_pct is not None else None
        ),
        plan=plan,
    )


async def set_avatar_path(
    session: AsyncSession, telegram_id: int, avatar_path: str | None
) -> bool:
    user = await get_by_telegram_id(session, telegram_id)
    if user is None:
        return False
    user.avatar_path = avatar_path
    await session.flush()
    return True


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
) -> tuple[User, NutritionPlan, float | None]:
    plan = build_nutrition_plan(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        activity=activity,
        goal=goal,
    )
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

    await _upsert_measurement(
        session,
        user.id,
        weight_kg=weight_kg,
    )
    await session.flush()

    return user, plan, None


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
        )

    plan = build_nutrition_plan(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        activity=activity,
        goal=goal,
    )
    user.name = name
    user.gender = gender
    user.age = age
    user.height_cm = Decimal(str(height_cm))
    user.activity_level = activity
    user.goal = goal
    user.tdee = Decimal(str(plan.tdee))
    user.target_kcal = Decimal(str(plan.target_kcal))
    user.target_protein = Decimal(str(plan.macros.protein_g))
    user.target_carb = Decimal(str(plan.macros.carb_g))
    user.target_fat = Decimal(str(plan.macros.fat_g))

    await _upsert_measurement(
        session,
        user.id,
        weight_kg=weight_kg,
    )
    await session.flush()

    return user, plan, None
