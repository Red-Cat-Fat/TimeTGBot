from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.db.repositories.timezones import TimezoneRepository
from bot.handlers.commands import ADD_MY_TIME_CALLBACK_PREFIX, UTC_MAX_OFFSET, UTC_MIN_OFFSET

ADD_MY_TIME_CALLBACK_RE = re.compile(rf"^{ADD_MY_TIME_CALLBACK_PREFIX}:([+-]?\d{{1,2}})$")


def create_callbacks_router(session_factory: async_sessionmaker) -> Router:
    router = Router()

    @router.callback_query(F.data.startswith(ADD_MY_TIME_CALLBACK_PREFIX))
    async def add_my_time_callback_handler(callback: CallbackQuery) -> None:
        if callback.data is None or callback.from_user is None or callback.message is None:
            await callback.answer("Некорректный callback payload.", show_alert=True)
            return

        callback_match = ADD_MY_TIME_CALLBACK_RE.match(callback.data)
        if callback_match is None:
            await callback.answer("Некорректный callback payload.", show_alert=True)
            return

        if callback.message.reply_markup is None:
            await callback.answer("Вы уже выбрали UTC.")
            return

        selected_offset = int(callback_match.group(1))
        if selected_offset < UTC_MIN_OFFSET or selected_offset > UTC_MAX_OFFSET:
            await callback.answer("Некорректный UTC offset.", show_alert=True)
            return

        async with session_factory() as session:
            timezone_repository = TimezoneRepository(session)
            await timezone_repository.set_user_timezone(
                chat_id=callback.message.chat.id,
                user_id=callback.from_user.id,
                offset=selected_offset * 60,
            )

        await callback.answer("UTC сохранён")
        await callback.message.delete()

    return router
