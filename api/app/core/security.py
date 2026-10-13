import hmac

from fastapi import Header, HTTPException

from app.core.config import settings


async def require_api_key(x_api_key: str = Header(default="")) -> None:
    if not settings.api_key or not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
