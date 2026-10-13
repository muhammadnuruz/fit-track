from __future__ import annotations

import asyncio
import hmac
from collections.abc import Awaitable, Callable

import structlog
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.cache import get_redis
from app.config import settings
from app.db.session import engine

log = structlog.get_logger(__name__)


def create_app(bot: Bot, dp: Dispatcher) -> FastAPI:
    app = FastAPI(title="FitTrack API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.bot = bot
    app.state.dp = dp
    app.state.bg_tasks = set()

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.get("/health")
    async def health() -> dict[str, str]:
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            redis = get_redis()
            if redis is not None:
                await redis.ping()
        except Exception as exc:
            log.warning("health_check_failed", error=str(exc))
            raise HTTPException(status_code=503, detail="Service unavailable") from exc
        return {"status": "ok"}

    if settings.bot_mode == "webhook":
        if not settings.webhook_secret:
            raise RuntimeError(
                "webhook rejimida WEBHOOK_SECRET majburiy (soxta update'lardan himoya)"
            )

        async def _feed(update: Update) -> None:
            try:
                await dp.feed_update(bot, update)
            except Exception as exc:
                log.warning("webhook_feed_failed", error=str(exc))

        @app.post(settings.webhook_path)
        async def telegram_webhook(request: Request) -> JSONResponse:
            header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if not hmac.compare_digest(header, settings.webhook_secret):
                return JSONResponse({"ok": False}, status_code=403)
            payload = await request.json()
            update = Update.model_validate(payload, context={"bot": bot})
            task = asyncio.create_task(_feed(update))
            app.state.bg_tasks.add(task)
            task.add_done_callback(app.state.bg_tasks.discard)
            return JSONResponse({"ok": True})

    return app
