from __future__ import annotations

import asyncio
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_telegram_id
from app.api.schemas import MacrosOut, MeOut, MeProfileOut, PlanOut, ProfileIn
from app.core.formulas import NutritionPlan
from app.db.session import get_session
from app.services.users import (
    ProfileData,
    load_profile,
    set_avatar_path,
    update_from_onboarding,
)

router = APIRouter(prefix="/api/me")

# Avatar yuklash cheklovlari
_ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
_MAX_BYTES = 3 * 1024 * 1024  # 3 MB

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"
AVATAR_DIR = UPLOAD_ROOT / "avatars"


def _plan_out(plan: NutritionPlan, body_fat_pct: float | None) -> PlanOut:
    return PlanOut(
        bmr=plan.bmr,
        tdee=plan.tdee,
        target_kcal=plan.target_kcal,
        bmi=plan.bmi,
        body_fat_pct=body_fat_pct,
        macros=MacrosOut(
            kcal=plan.macros.kcal,
            protein_g=plan.macros.protein_g,
            carb_g=plan.macros.carb_g,
            fat_g=plan.macros.fat_g,
        ),
    )


def _me_out(data: ProfileData) -> MeOut:
    avatar_url: str | None = None
    if data.user.avatar_path:
        fpath = AVATAR_DIR / data.user.avatar_path.rsplit("/", 1)[-1]
        version = int(fpath.stat().st_mtime) if fpath.exists() else 0
        avatar_url = f"{data.user.avatar_path}?v={version}"
    profile = MeProfileOut(
        name=data.user.name,
        gender=data.user.gender,
        age=data.user.age,
        height_cm=float(data.user.height_cm),
        weight_kg=data.weight_kg,
        activity=data.user.activity_level,
        goal=data.user.goal,
        avatar_url=avatar_url,
    )
    plan = _plan_out(data.plan, data.body_fat_pct) if data.plan is not None else None
    return MeOut(registered=True, profile=profile, plan=plan)


@router.get("", response_model=MeOut)
async def get_me(
    telegram_id: int = Depends(require_telegram_id),
    session: AsyncSession = Depends(get_session),
) -> MeOut:
    data = await load_profile(session, telegram_id)
    if data is None:
        return MeOut(registered=False)
    return _me_out(data)


@router.patch("", response_model=MeOut)
async def patch_me(
    payload: ProfileIn,
    telegram_id: int = Depends(require_telegram_id),
    session: AsyncSession = Depends(get_session),
) -> MeOut:
    await update_from_onboarding(
        session,
        telegram_id,
        name=payload.name.strip(),
        gender=payload.gender,
        age=payload.age,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        activity=payload.activity,
        goal=payload.goal,
    )
    await session.commit()
    data = await load_profile(session, telegram_id)
    if data is None:  # amalda bo'lmaydi (endigina yozdik)
        raise HTTPException(status_code=404, detail="Profil topilmadi")
    return _me_out(data)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile,
    telegram_id: int = Depends(require_telegram_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    ext = _ALLOWED.get(file.content_type or "")
    if ext is None:
        raise HTTPException(status_code=415, detail="Faqat JPEG, PNG yoki WEBP")
    data = await file.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="Rasm 3 MB dan katta")
    if not data:
        raise HTTPException(status_code=400, detail="Bo'sh fayl")

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{telegram_id}-{uuid4().hex}.{ext}"
    avatar_path = AVATAR_DIR / filename
    old_files = list(AVATAR_DIR.glob(f"{telegram_id}.*"))
    await asyncio.to_thread(avatar_path.write_bytes, data)

    url_path = f"/avatars/{filename}"
    if not await set_avatar_path(session, telegram_id, url_path):
        await asyncio.to_thread(avatar_path.unlink, missing_ok=True)
        raise HTTPException(status_code=404, detail="Avval ro'yxatdan o'ting")
    try:
        await session.commit()
    except Exception:
        await asyncio.to_thread(avatar_path.unlink, missing_ok=True)
        raise
    for old in old_files:
        if old != avatar_path:
            await asyncio.to_thread(old.unlink, missing_ok=True)
    return {"url": f"{url_path}?v={int(time.time())}"}


@router.delete("/avatar")
async def delete_avatar(
    telegram_id: int = Depends(require_telegram_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    old_files = list(AVATAR_DIR.glob(f"{telegram_id}.*"))
    await set_avatar_path(session, telegram_id, None)
    await session.commit()
    for old in old_files:
        await asyncio.to_thread(old.unlink, missing_ok=True)
    return {"ok": True}
