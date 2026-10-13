import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.api_client import ApiClient
from app.bot import create_bot, create_dispatcher
from app.commands import setup_bot_commands
from app.config import settings, validate_settings

log = logging.getLogger(__name__)


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("bot polling started")
    await dp.start_polling(bot)


async def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(
        url=url,
        secret_token=settings.webhook_secret,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=settings.webhook_secret).register(
        app, path=settings.webhook_path
    )
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host=settings.web_host, port=settings.web_port).start()
    log.info("bot webhook listening on %s:%s, url=%s", settings.web_host, settings.web_port, url)
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


async def run() -> None:
    bot = create_bot()
    api = ApiClient(settings.api_base_url, settings.api_key)
    dp = create_dispatcher(api)
    try:
        await setup_bot_commands(bot)
        if settings.bot_mode == "webhook":
            await run_webhook(bot, dp)
        else:
            await run_polling(bot, dp)
    finally:
        await api.close()
        await bot.session.close()
        log.info("bot stopped")


def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    errors = validate_settings(settings)
    if errors:
        for error in errors:
            log.error("config: %s", error)
        raise SystemExit(1)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run())


if __name__ == "__main__":
    main()
