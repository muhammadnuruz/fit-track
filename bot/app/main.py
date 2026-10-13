import asyncio
import contextlib
import logging

from app.api_client import ApiClient
from app.bot import create_bot, create_dispatcher
from app.commands import setup_bot_commands
from app.config import settings

log = logging.getLogger(__name__)


async def run() -> None:
    bot = create_bot()
    api = ApiClient(settings.api_base_url, settings.api_key)
    dp = create_dispatcher(api)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await setup_bot_commands(bot)
        log.info("bot polling started, api=%s", settings.api_base_url)
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()
        log.info("bot stopped")


def main() -> None:
    logging.basicConfig(
        level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    if not settings.bot_token or not settings.api_key:
        log.error("BOT_TOKEN and API_KEY must be set (see .env.example)")
        raise SystemExit(1)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run())


if __name__ == "__main__":
    main()
