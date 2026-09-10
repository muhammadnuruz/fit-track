from __future__ import annotations

from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.onboarding import router as onboarding_router
from app.config import settings

WEBAPP_DIR = Path(__file__).parent / "webapp"


def create_app(bot: Bot, dp: Dispatcher) -> FastAPI:
    app = FastAPI(title="FitTrack API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.bot = bot
    app.state.dp = dp
    app.include_router(onboarding_router)

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
        html = (WEBAPP_DIR / "landing.html").read_text(encoding="utf-8")
        bot_link = (
            f"https://t.me/{settings.bot_username.lstrip('@')}"
            if settings.bot_username
            else "#"
        )
        return HTMLResponse(html.replace("__BOT_LINK__", bot_link))

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/webapp")
    async def webapp_page() -> FileResponse:
        return FileResponse(WEBAPP_DIR / "index.html")

    app.mount("/assets", StaticFiles(directory=WEBAPP_DIR / "assets"), name="assets")

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
