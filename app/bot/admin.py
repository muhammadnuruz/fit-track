from __future__ import annotations

import asyncio

import structlog
from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import func, select

from app.bot.access import is_admin
from app.bot.emoji import (
    ADMIN_PANEL_EMOJI_ID,
    BLOCKED_EMOJI_ID,
    BROADCAST_START_EMOJI_ID,
    CHANGE_LANG_EMOJI_ID,
    CHECK_EMOJI_ID,
    DELETE_EMOJI_ID,
    ERROR_EMOJI_ID,
    FLAG_EMOJI_IDS,
    STATISTICS_EMOJI_ID,
    custom_emoji,
)
from app.bot.handlers.common import _send_language_picker, _send_welcome
from app.bot.keyboards.admin import (
    BACK_ADMIN_MENU,
    BACK_MAIN_MENU,
    BROADCAST_BTN,
    DELETE_USER_BTN,
    STATS_BTN,
    admin_menu_keyboard,
    broadcast_keyboard,
)
from app.bot.states import AdminBroadcast, AdminDeleteUser
from app.db.session import async_session_factory
from app.i18n import Lang
from app.models import User, UserSettings
from app.services.users import delete_user_completely

log = structlog.get_logger(__name__)

router = Router(name="admin")

_SEND_DELAY_S = 0.33
_background_tasks: set[asyncio.Task[None]] = set()


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await message.answer(
        f"{custom_emoji(ADMIN_PANEL_EMOJI_ID, '👨‍💻')} Admin panel",
        reply_markup=admin_menu_keyboard(),
    )


@router.message(F.text == BACK_MAIN_MENU)
async def admin_back_to_main_menu(message: Message, state: FSMContext, lang: Lang | None) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return
    await state.clear()
    if lang is None:
        await _send_language_picker(message)
        return
    await _send_welcome(message, lang)


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
        f"{custom_emoji(STATISTICS_EMOJI_ID, '📊')} Statistics\n\n"
        f"{custom_emoji('5936283232780684228', '👥')} Total users: {total_users}\n"
        f"{custom_emoji(CHECK_EMOJI_ID, '✅')} Profiles: {completed}\n\n"
        f"{custom_emoji(CHANGE_LANG_EMOJI_ID, '🌍')} By language:\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.UZ], '🇺🇿')} uz: {per_lang.get(Lang.UZ, 0)}\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.RU], '🇷🇺')} ru: {per_lang.get(Lang.RU, 0)}\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.EN], '🇬🇧')} en: {per_lang.get(Lang.EN, 0)}"
    )
    await message.answer(text, reply_markup=admin_menu_keyboard())


@router.message(F.text == BROADCAST_BTN)
async def admin_broadcast_start(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.set_state(AdminBroadcast.waiting_message)
    await message.answer(
        '<tg-emoji emoji-id="5370599459661045441">📢</tg-emoji> '
        "Send the message to broadcast to every user.\n\n"
        "Any type works: text, photo, video, document, a message with inline "
        "buttons, or a forward.",
        reply_markup=broadcast_keyboard(),
    )


@router.message(AdminBroadcast.waiting_message, F.text == BACK_ADMIN_MENU)
async def admin_broadcast_back(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.clear()
    await cmd_admin(message)


@router.message(F.text == DELETE_USER_BTN)
async def admin_delete_user_start(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.set_state(AdminDeleteUser.waiting_user_id)
    await message.answer(
        f"{custom_emoji(DELETE_EMOJI_ID, '🗑')} Send the user ID to delete.\n\n"
        "The user and all their data will be permanently removed.",
        reply_markup=broadcast_keyboard(),
    )


@router.message(AdminDeleteUser.waiting_user_id, F.text == BACK_ADMIN_MENU)
async def admin_delete_user_back(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.clear()
    await cmd_admin(message)


@router.message(AdminDeleteUser.waiting_user_id)
async def admin_delete_user_receive(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} ID must be a number. Try again.",
            reply_markup=broadcast_keyboard(),
        )
        return
    telegram_id = int(raw)
    await state.clear()
    async with async_session_factory() as session:
        deleted = await delete_user_completely(session, telegram_id)
    if deleted:
        await message.answer(
            f"{custom_emoji(CHECK_EMOJI_ID, '✅')} User <code>{telegram_id}</code> deleted.",
            reply_markup=admin_menu_keyboard(),
        )
    else:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} User <code>{telegram_id}</code> not found.",
            reply_markup=admin_menu_keyboard(),
        )


@router.message(AdminBroadcast.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        return
    await state.clear()
    async with async_session_factory() as session:
        telegram_ids = (await session.execute(select(UserSettings.telegram_id))).scalars().all()

    if not telegram_ids:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} No users in the database yet.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    status = await message.answer(
        f"{custom_emoji(BROADCAST_START_EMOJI_ID, '🚀')} Broadcast started — "
        f"{len(telegram_ids)} users.\n"
        "This runs in the background; you don't need to wait.",
        reply_markup=admin_menu_keyboard(),
    )
    task = asyncio.create_task(_run_broadcast(message, status, list(telegram_ids)))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def _run_broadcast(
    source: Message,
    status: Message,
    telegram_ids: list[int],
) -> None:
    total = len(telegram_ids)
    sent = 0
    failed = 0
    blocked = 0

    for index, telegram_id in enumerate(telegram_ids, start=1):
        try:
            await source.copy_to(chat_id=telegram_id)
            sent += 1
        except TelegramRetryAfter as exc:
            log.warning("broadcast_retry_after", retry_after=exc.retry_after)
            await asyncio.sleep(exc.retry_after + 1)
            try:
                await source.copy_to(chat_id=telegram_id)
                sent += 1
            except Exception as retry_exc:
                failed += 1
                log.warning(
                    "broadcast_retry_failed",
                    telegram_id=telegram_id,
                    error=str(retry_exc),
                )
        except TelegramForbiddenError:
            failed += 1
            blocked += 1
            log.warning("broadcast_user_blocked", telegram_id=telegram_id)
        except Exception as exc:
            failed += 1
            log.warning("broadcast_failed", telegram_id=telegram_id, error=str(exc))

        await asyncio.sleep(_SEND_DELAY_S)

        if index % 25 == 0 or index == total:
            try:
                await status.edit_text(
                    f"{custom_emoji(BROADCAST_START_EMOJI_ID, '🚀')} Broadcasting\n"
                    f"{custom_emoji(STATISTICS_EMOJI_ID, '📊')} Total: {total}\n"
                    f"{custom_emoji(CHECK_EMOJI_ID, '✅')} Sent: {sent}\n"
                    f"{custom_emoji(ERROR_EMOJI_ID, '❌')} Failed: {failed}\n"
                    f"⏳ Progress: {index}/{total}"
                )
            except Exception as exc:
                log.warning("broadcast_status_update_failed", error=str(exc))

    report = (
        f"{custom_emoji(CHECK_EMOJI_ID, '✅')} Broadcast finished!\n\n"
        f"{custom_emoji(STATISTICS_EMOJI_ID, '📊')} Total: {total}\n"
        f"{custom_emoji(CHECK_EMOJI_ID, '✅')} Sent: {sent}\n"
        f"{custom_emoji(ERROR_EMOJI_ID, '❌')} Failed: {failed}\n"
        f"{custom_emoji(BLOCKED_EMOJI_ID, '🚫')} Blocked: {blocked}"
    )
    try:
        await status.edit_text(report)
    except Exception as exc:
        log.warning("broadcast_final_status_failed", error=str(exc))
    try:
        await source.answer(report, reply_markup=admin_menu_keyboard())
    except Exception as exc:
        log.warning("broadcast_summary_failed", error=str(exc))
