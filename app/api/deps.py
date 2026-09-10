from __future__ import annotations

from fastapi import Header, HTTPException

from app.api.security import InitDataError, validate_init_data
from app.config import settings


async def require_telegram_id(x_init_data: str = Header(default="", alias="X-Init-Data")) -> int:
    """Mini App'ning X-Init-Data header'idagi Telegram initData'ni tekshiradi.
    To'g'ri bo'lsa telegram_id qaytaradi, aks holda 401."""
    try:
        init = validate_init_data(
            x_init_data,
            settings.bot_token,
            max_age_seconds=settings.init_data_max_age_seconds,
        )
    except InitDataError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return init.user_id
