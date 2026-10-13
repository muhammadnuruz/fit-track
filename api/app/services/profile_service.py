from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.formulas import NutritionPlan, build_nutrition_plan
from app.models.measurement import Measurement
from app.models.user import User
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.user_repository import UserRepository
from app.schemas.profile import MacrosOut, PlanOut, ProfileIn, ProfileOut


def today_local() -> date:
    return datetime.now(ZoneInfo(settings.tz)).date()


def _plan_for(user: User, weight_kg: float) -> NutritionPlan:
    return build_nutrition_plan(
        weight_kg=weight_kg,
        height_cm=float(user.height_cm),
        age=user.age,
        gender=user.gender,
        activity=user.activity_level,
        goal=user.goal,
    )


def _to_out(user: User, weight_kg: float | None) -> ProfileOut:
    plan = None
    if weight_kg is not None:
        computed = _plan_for(user, weight_kg)
        plan = PlanOut(
            bmr=computed.bmr,
            tdee=computed.tdee,
            target_kcal=computed.target_kcal,
            bmi=computed.bmi,
            macros=MacrosOut(
                kcal=computed.macros.kcal,
                protein_g=computed.macros.protein_g,
                carb_g=computed.macros.carb_g,
                fat_g=computed.macros.fat_g,
            ),
        )
    return ProfileOut(
        name=user.name,
        gender=user.gender,
        age=user.age,
        height_cm=float(user.height_cm),
        weight_kg=weight_kg,
        activity=user.activity_level,
        goal=user.goal,
        plan=plan,
    )


async def upsert_profile(session: AsyncSession, telegram_id: int, payload: ProfileIn) -> ProfileOut:
    users = UserRepository(session)
    measurements = MeasurementRepository(session)
    plan = build_nutrition_plan(
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        age=payload.age,
        gender=payload.gender,
        activity=payload.activity,
        goal=payload.goal,
    )

    user = await users.get_by_telegram_id(telegram_id)
    if user is None:
        user = User(telegram_id=telegram_id)
        users.add(user)
    user.name = payload.name
    user.gender = payload.gender
    user.age = payload.age
    user.height_cm = Decimal(str(payload.height_cm))
    user.activity_level = payload.activity
    user.goal = payload.goal
    user.tdee = Decimal(str(plan.tdee))
    user.target_kcal = Decimal(str(plan.target_kcal))
    user.target_protein = Decimal(str(plan.macros.protein_g))
    user.target_carb = Decimal(str(plan.macros.carb_g))
    user.target_fat = Decimal(str(plan.macros.fat_g))

    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Profile is being created, retry") from exc

    today = today_local()
    measurement = await measurements.for_day(user.id, today)
    if measurement is None:
        measurement = Measurement(user_id=user.id, date=today)
        measurements.add(measurement)
    measurement.weight_kg = Decimal(str(payload.weight_kg))
    await session.commit()

    return _to_out(user, payload.weight_kg)


async def get_profile(session: AsyncSession, telegram_id: int) -> ProfileOut | None:
    user = await UserRepository(session).get_by_telegram_id(telegram_id)
    if user is None:
        return None
    latest = await MeasurementRepository(session).latest_for_user(user.id)
    weight = float(latest.weight_kg) if latest is not None else None
    return _to_out(user, weight)
