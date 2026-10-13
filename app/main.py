from __future__ import annotations

import asyncio
import contextlib

import uvicorn

from app.api.app import create_app
from app.bot.bot import create_bot, create_dispatcher
from app.bot.commands import setup_bot_commands
from app.config import settings
from app.logging_config import get_logger, setup_logging

log = get_logger(__name__)


async def run() -> None:
    bot = create_bot()
    dp = create_dispatcher()
    await setup_bot_commands(bot)

    app = create_app(bot, dp)
    server = uvicorn.Server(
        uvicorn.Config(app, host=settings.api_host, port=settings.api_port, log_config=None)
    )

    if settings.bot_mode == "webhook":
        log.info("bot.starting", mode="webhook")
        if settings.webhook_url:
            url = settings.webhook_url.rstrip("/") + settings.webhook_path
            await bot.set_webhook(
                url=url,
                secret_token=settings.webhook_secret or None,
                drop_pending_updates=True,
            )
            log.info("webhook.set", url=url)
        try:
            await server.serve()
        finally:
            await bot.session.close()
            log.info("bot.stopped")
        return

    log.info("bot.starting", mode="polling")
    await bot.delete_webhook(drop_pending_updates=True)
    polling = asyncio.create_task(dp.start_polling(bot))
    try:
        await server.serve()
    finally:
        polling.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await polling
        await bot.session.close()
        log.info("bot.stopped")


def main() -> None:
    setup_logging()
    if not settings.bot_token:
        log.error("config.missing", detail="BOT_TOKEN o'rnatilmagan (.env ni to'ldiring)")
        raise SystemExit(1)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run())


if __name__ == "__main__":
    main()
