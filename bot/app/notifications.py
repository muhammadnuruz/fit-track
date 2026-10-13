import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import User

from app.config import settings
from app.emoji import NEW_USER_EMOJI_ID, custom_emoji
from app.i18n import Lang

log = logging.getLogger(__name__)


def _new_user_text(user: User, lang: Lang, *, plain: bool) -> str:
    username = f"@{user.username}" if user.username else "—"
    prefix = "🆕" if plain else custom_emoji(NEW_USER_EMOJI_ID, "🆕")
    return (
        f"{prefix} New user joined\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Name: {user.full_name}\n"
        f"Username: {username}\n"
        f"Language: {lang.value}"
    )


async def notify_admins_new_user(bot: Bot, user: User, lang: Lang) -> None:
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=_new_user_text(user, lang, plain=False))
        except TelegramBadRequest:
            try:
                await bot.send_message(
                    chat_id=admin_id, text=_new_user_text(user, lang, plain=True)
                )
            except Exception as exc:
                log.warning("admin notify failed for %s: %s", admin_id, exc)
        except Exception as exc:
            log.warning("admin notify failed for %s: %s", admin_id, exc)
