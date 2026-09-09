from __future__ import annotations

from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from app.api.routes.onboarding import router as onboarding_router
from app.config import settings

WEBAPP_DIR = Path(__file__).parent / "webapp"


def create_app(bot: Bot, dp: Dispatcher) -> FastAPI:
    app = FastAPI(title="FitTrack API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.bot = bot
    app.state.dp = dp
    app.include_router(onboarding_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/webapp")
    async def webapp_page() -> FileResponse:
        return FileResponse(WEBAPP_DIR / "index.html")

    if settings.bot_mode == "webhook":

        @app.post(settings.webhook_path)
        async def telegram_webhook(request: Request) -> JSONResponse:
            if settings.webhook_secret:
                header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if header != settings.webhook_secret:
                    return JSONResponse({"ok": False}, status_code=403)
            payload = await request.json()
            update = Update.model_validate(payload, context={"bot": bot})
            await dp.feed_update(bot, update)
            return JSONResponse({"ok": True})

    return app
