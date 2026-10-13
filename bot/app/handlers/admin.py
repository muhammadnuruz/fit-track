import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.access import is_admin
from app.api_client import ApiClient, ApiError
from app.emoji import (
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
from app.handlers.common import send_language_picker, send_welcome
from app.i18n import Lang
from app.keyboards.admin import (
    BACK_ADMIN_MENU,
    BACK_MAIN_MENU,
    BROADCAST_BTN,
    DELETE_USER_BTN,
    STATS_BTN,
    admin_menu_keyboard,
    broadcast_keyboard,
)
from app.states import AdminBroadcast, AdminDeleteUser

router = Router(name="admin")
log = logging.getLogger(__name__)

_SEND_DELAY_S = 0.33
_background_tasks: set[asyncio.Task[None]] = set()


def _sender_is_admin(message: Message) -> bool:
    return is_admin(message.from_user.id if message.from_user else None)


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not _sender_is_admin(message):
        return
    await message.answer(
        f"{custom_emoji(ADMIN_PANEL_EMOJI_ID, '👨‍💻')} Admin panel",
        reply_markup=admin_menu_keyboard(),
    )


@router.message(F.text == BACK_MAIN_MENU)
async def admin_back_to_main_menu(message: Message, state: FSMContext, lang: Lang | None) -> None:
    if not _sender_is_admin(message):
        return
    await state.clear()
    if lang is None:
        await send_language_picker(message)
        return
    await send_welcome(message, lang)


@router.message(F.text == STATS_BTN)
async def admin_stats(message: Message, api: ApiClient) -> None:
    if not _sender_is_admin(message):
        return
    try:
        stats = await api.get_stats()
    except ApiError:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} API unavailable.",
            reply_markup=admin_menu_keyboard(),
        )
        return
    by_language = stats["by_language"]
    text = (
        f"{custom_emoji(STATISTICS_EMOJI_ID, '📊')} Statistics\n\n"
        f"{custom_emoji('5936283232780684228', '👥')} Total users: {stats['total_users']}\n"
        f"{custom_emoji(CHECK_EMOJI_ID, '✅')} Profiles: {stats['profiles']}\n\n"
        f"{custom_emoji(CHANGE_LANG_EMOJI_ID, '🌍')} By language:\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.UZ], '🇺🇿')} uz: {by_language.get('uz', 0)}\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.RU], '🇷🇺')} ru: {by_language.get('ru', 0)}\n"
        f"{custom_emoji(FLAG_EMOJI_IDS[Lang.EN], '🇬🇧')} en: {by_language.get('en', 0)}"
    )
    await message.answer(text, reply_markup=admin_menu_keyboard())


@router.message(F.text == BROADCAST_BTN)
async def admin_broadcast_start(message: Message, state: FSMContext) -> None:
    if not _sender_is_admin(message):
        return
    await state.set_state(AdminBroadcast.waiting_message)
    await message.answer(
        f"{custom_emoji('5370599459661045441', '📢')} "
        "Send the message to broadcast to every user.\n\n"
        "Any type works: text, photo, video, document, a message with inline "
        "buttons, or a forward.",
        reply_markup=broadcast_keyboard(),
    )


@router.message(AdminBroadcast.waiting_message, F.text == BACK_ADMIN_MENU)
async def admin_broadcast_back(message: Message, state: FSMContext) -> None:
    if not _sender_is_admin(message):
        return
    await state.clear()
    await cmd_admin(message)


@router.message(AdminBroadcast.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, api: ApiClient) -> None:
    if not _sender_is_admin(message):
        return
    await state.clear()
    try:
        telegram_ids = await api.list_telegram_ids()
    except ApiError:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} API unavailable.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    if not telegram_ids:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} No users yet.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    status = await message.answer(
        f"{custom_emoji(BROADCAST_START_EMOJI_ID, '🚀')} Broadcast started — "
        f"{len(telegram_ids)} users.\n"
        "This runs in the background; you don't need to wait.",
        reply_markup=admin_menu_keyboard(),
    )
    task = asyncio.create_task(_run_broadcast(message, status, telegram_ids))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


@router.message(F.text == DELETE_USER_BTN)
async def admin_delete_user_start(message: Message, state: FSMContext) -> None:
    if not _sender_is_admin(message):
        return
    await state.set_state(AdminDeleteUser.waiting_user_id)
    await message.answer(
        f"{custom_emoji(DELETE_EMOJI_ID, '🗑')} Send the user ID to delete.\n\n"
        "The user and all their data will be permanently removed.",
        reply_markup=broadcast_keyboard(),
    )


@router.message(AdminDeleteUser.waiting_user_id, F.text == BACK_ADMIN_MENU)
async def admin_delete_user_back(message: Message, state: FSMContext) -> None:
    if not _sender_is_admin(message):
        return
    await state.clear()
    await cmd_admin(message)


@router.message(AdminDeleteUser.waiting_user_id)
async def admin_delete_user_receive(message: Message, state: FSMContext, api: ApiClient) -> None:
    if not _sender_is_admin(message):
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
    try:
        deleted = await api.delete_user(telegram_id)
    except ApiError:
        await message.answer(
            f"{custom_emoji(ERROR_EMOJI_ID, '❌')} API unavailable.",
            reply_markup=admin_menu_keyboard(),
        )
        return
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


async def _run_broadcast(source: Message, status: Message, telegram_ids: list[int]) -> None:
    total = len(telegram_ids)
    sent = 0
    failed = 0
    blocked = 0

    for index, telegram_id in enumerate(telegram_ids, start=1):
        try:
            await source.copy_to(chat_id=telegram_id)
            sent += 1
        except TelegramRetryAfter as exc:
            log.warning("broadcast retry after %s", exc.retry_after)
            await asyncio.sleep(exc.retry_after + 1)
            try:
                await source.copy_to(chat_id=telegram_id)
                sent += 1
            except Exception as retry_exc:
                failed += 1
                log.warning("broadcast retry failed for %s: %s", telegram_id, retry_exc)
        except TelegramForbiddenError:
            failed += 1
            blocked += 1
        except Exception as exc:
            failed += 1
            log.warning("broadcast failed for %s: %s", telegram_id, exc)

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
                log.warning("broadcast status update failed: %s", exc)

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
        log.warning("broadcast final status failed: %s", exc)
    try:
        await source.answer(report, reply_markup=admin_menu_keyboard())
    except Exception as exc:
        log.warning("broadcast summary failed: %s", exc)
