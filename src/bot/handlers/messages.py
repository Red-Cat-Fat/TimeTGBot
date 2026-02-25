from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.services.time_conversion import TimeConversionService
from bot.handlers.commands import SET_MY_TIME_CALLBACK_PREFIX

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")


def _build_timezone_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for hour in range(-12, 15):
        sign = "+" if hour >= 0 else ""
        tz_label = f"UTC {sign}{hour}"
        callback_data = f"{SET_MY_TIME_CALLBACK_PREFIX}:{hour:+d}"
        row.append(InlineKeyboardButton(text=tz_label, callback_data=callback_data))
        if len(row) == 4:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_messages_router(session_factory: async_sessionmaker) -> Router:
    router = Router()
    service = TimeConversionService(session_factory)

    @router.message(F.text)
    async def convert_time_for_chat(message: Message) -> None:
        if message.text is None or message.from_user is None:
            return

        time_match = TIME_RE.search(message.text)
        if time_match is None:
            return

        sender_id = message.from_user.id
        chat_id = message.chat.id
        sender_timezone = await service.get_sender_timezone(user_id=sender_id, chat_id=chat_id)
        if sender_timezone is None:
            await message.reply(
                "Вы не указали свой UTC.",
                reply_markup=_build_timezone_keyboard(),
            )
            return

        chat_timezones = await service.get_chat_timezones(chat_id=chat_id)
        if not chat_timezones:
            return

        source_time = time_match.group(0)
        lines = []
        for timezone in chat_timezones:
            local_time = service.convert_time(
                source_time=source_time,
                sender_timezone=sender_timezone,
                target_timezone=timezone,
            )
            lines.append(f"{timezone.label} {local_time}")

        if not lines:
            return

        await message.reply("\n".join(lines))
    return router
