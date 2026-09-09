from __future__ import annotations

import asyncio
import contextlib

from app.bot.bot import create_bot, create_dispatcher
from app.bot.commands import setup_bot_commands
from app.config import settings
from app.logging_config import get_logger, setup_logging

log = get_logger(__name__)


async def run_polling() -> None:
    bot = create_bot()
    dp = create_dispatcher()
    log.info("bot.starting", mode="polling")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await setup_bot_commands(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        log.info("bot.stopped")


def main() -> None:
    setup_logging()
    if not settings.bot_token:
        log.error("config.missing", detail="BOT_TOKEN o'rnatilmagan (.env ni to'ldiring)")
        raise SystemExit(1)

    if settings.bot_mode == "polling":
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(run_polling())
    else:
        raise NotImplementedError("webhook rejimi hali ulanmagan — BOT_MODE=polling ishlating")


if __name__ == "__main__":
    main()
