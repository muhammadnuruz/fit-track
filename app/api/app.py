from __future__ import annotations

import asyncio
import hmac
from collections.abc import Awaitable, Callable
from pathlib import Path

import structlog
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.me import AVATAR_DIR
from app.api.routes.me import router as me_router
from app.api.routes.onboarding import router as onboarding_router
from app.config import settings

log = structlog.get_logger(__name__)

WEBAPP_DIR = Path(__file__).parent / "webapp"

# Telegram mini-app iframe'da ochilgani uchun X-Frame-Options: DENY QO'YMAYMIZ.
_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://telegram.org https://yandex.ru "
    "https://*.yandex.net; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https://yandex.ru https://*.yandex.ru https://*.yandex.net; "
    "frame-src https://yandex.ru https://*.yandex.net; "
    "base-uri 'self'; object-src 'none'"
)


def _render_landing() -> str:
    """landing.html ni bir marta o'qib, bot linkini joylaymiz (har so'rovда disk o'qilmaydi)."""
    html = (WEBAPP_DIR / "landing.html").read_text(encoding="utf-8")
    bot_link = (
        f"https://t.me/{settings.bot_username.lstrip('@')}" if settings.bot_username else "#"
    )
    return html.replace("__BOT_LINK__", bot_link)


def create_app(bot: Bot, dp: Dispatcher) -> FastAPI:
    app = FastAPI(title="FitTrack API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.bot = bot
    app.state.dp = dp
    app.state.landing_html = _render_landing()  # startup'da bir marta render
    app.state.bg_tasks = set()  # background task'larга referens (GC'dan saqlash)
    app.include_router(onboarding_router)
    app.include_router(me_router)

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", _CSP)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid request payload",
                "errors": [
                    {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
                    for error in exc.errors()
                ],
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.get("/", response_class=HTMLResponse)
    async def landing_page() -> HTMLResponse:
        return HTMLResponse(app.state.landing_html)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/webapp")
    async def webapp_page() -> FileResponse:
        return FileResponse(WEBAPP_DIR / "index.html")

    app.mount("/assets", StaticFiles(directory=WEBAPP_DIR / "assets"), name="assets")
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)  # yuklangan avatarlar (doimiy volume)
    app.mount("/avatars", StaticFiles(directory=AVATAR_DIR), name="avatars")

    if settings.bot_mode == "webhook":
        # Webhook rejimida secret majburiy — bo'lmasa soxta update yuborilishi mumkin.
        if not settings.webhook_secret:
            raise RuntimeError(
                "webhook rejimida WEBHOOK_SECRET majburiy (soxta update'lardan himoya)"
            )

        async def _feed(update: Update) -> None:
            try:
                await dp.feed_update(bot, update)
            except Exception as exc:  # background — javobni bloklamaydi
                log.warning("webhook_feed_failed", error=str(exc))

        @app.post(settings.webhook_path)
        async def telegram_webhook(request: Request) -> JSONResponse:
            header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if not hmac.compare_digest(header, settings.webhook_secret):
                return JSONResponse({"ok": False}, status_code=403)
            payload = await request.json()
            update = Update.model_validate(payload, context={"bot": bot})
            # Darrov 200 qaytaramiz; qayta ishlash background'da (Telegram qayta yuboradi).
            task = asyncio.create_task(_feed(update))
            app.state.bg_tasks.add(task)
            task.add_done_callback(app.state.bg_tasks.discard)
            return JSONResponse({"ok": True})

    return app
