from __future__ import annotations

import redis.asyncio as aioredis
import structlog

from app.config import settings

log = structlog.get_logger(__name__)

_client: aioredis.Redis | None = None
_initialized = False


def get_redis() -> aioredis.Redis | None:
    """Umumiy Redis klient (lazy). REDIS_URL bo'sh bo'lsa None — chaqiruvchi
    kod in-memory/DB fallback'ga o'tadi. Bir-instans deploy Redis'siz ham ishlaydi."""
    global _client, _initialized
    if not settings.redis_url:
        return None
    if not _initialized:
        _initialized = True
        try:
            _client = aioredis.from_url(settings.redis_url, decode_responses=True)
        except Exception as exc:
            log.warning("redis_init_failed", error=str(exc))
            _client = None
    return _client
