from __future__ import annotations

import structlog
from aiogram import Bot
from aiogram.types import User

from app.config import settings
from app.i18n import Lang

log = structlog.get_logger(__name__)


async def notify_admins_new_user(bot: Bot, user: User, lang: Lang) -> None:
    username = f"@{user.username}" if user.username else "—"
    text = (
        "🆕 Yangi foydalanuvchi qo'shildi\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Ism: {user.full_name}\n"
        f"Username: {username}\n"
        f"Til: {lang.value}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=text)
        except Exception as exc:
            log.warning("admin_notify_failed", admin_id=admin_id, error=str(exc))
