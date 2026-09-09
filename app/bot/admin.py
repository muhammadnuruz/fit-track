from __future__ import annotations

import structlog
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import func, select

from app.bot.access import is_admin
from app.bot.keyboards.admin import BROADCAST_BTN, STATS_BTN, admin_menu_keyboard
from app.bot.states import AdminBroadcast
from app.db.session import async_session_factory
from app.i18n import Lang
from app.models import User, UserSettings

log = structlog.get_logger(__name__)

router = Router(name="admin")


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await message.answer("👨‍💼 Admin panel", reply_markup=admin_menu_keyboard())


@router.message(F.text == STATS_BTN)
async def admin_stats(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    async with async_session_factory() as session:
        total_users = (
            await session.execute(select(func.count()).select_from(UserSettings))
        ).scalar_one()
        completed = (await session.execute(select(func.count()).select_from(User))).scalar_one()
        per_lang = {}
        for lang in Lang:
            count = (
                await session.execute(
                    select(func.count())
                    .select_from(UserSettings)
                    .where(UserSettings.language == lang)
                )
            ).scalar_one()
            per_lang[lang] = count
    text = (
        "📊 Statistika\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"✅ Profil to'ldirganlar: {completed}\n\n"
        "🌐 Til bo'yicha:\n"
        f"  🇺🇿 uz: {per_lang.get(Lang.UZ, 0)}\n"
        f"  🇷🇺 ru: {per_lang.get(Lang.RU, 0)}\n"
        f"  🇬🇧 en: {per_lang.get(Lang.EN, 0)}"
    )
    await message.answer(text, reply_markup=admin_menu_keyboard())


@router.message(F.text == BROADCAST_BTN)
async def admin_broadcast_start(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.set_state(AdminBroadcast.waiting_message)
    await message.answer("📢 Yubormoqchi bo'lgan xabaringizni yuboring (bekor qilish: /cancel)")


@router.message(Command("cancel"))
async def admin_cancel(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=admin_menu_keyboard())


@router.message(AdminBroadcast.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.clear()
    async with async_session_factory() as session:
        telegram_ids = (await session.execute(select(UserSettings.telegram_id))).scalars().all()
    sent = 0
    failed = 0
    for telegram_id in telegram_ids:
        try:
            await message.copy_to(chat_id=telegram_id)
            sent += 1
        except Exception as exc:
            failed += 1
            log.warning("broadcast_failed", telegram_id=telegram_id, error=str(exc))
    await message.answer(
        f"✅ Yuborildi: {sent}\n❌ Xato: {failed}", reply_markup=admin_menu_keyboard()
    )
