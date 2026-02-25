from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.services.time_conversion import TimeConversionService

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")
UTC_CALLBACK_RE = re.compile(r"^set_utc:(\d+):([+-]\d{1,2})$")


def _build_timezone_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for hour in range(-12, 15):
        sign = "+" if hour >= 0 else ""
        tz_label = f"UTC {sign}{hour}"
        callback_data = f"set_utc:{target_user_id}:{hour:+d}"
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

    @router.message(F.text.regexp(TIME_RE))
    async def convert_time_for_chat(message: Message) -> None:
        if message.text is None or message.from_user is None:
            return

        sender_id = message.from_user.id
        chat_id = message.chat.id
        sender_timezone = await service.get_sender_timezone(user_id=sender_id, chat_id=chat_id)
        if sender_timezone is None:
            await message.reply(
                "Вы не указали свой UTC.",
                reply_markup=_build_timezone_keyboard(target_user_id=sender_id),
            )
            return

        chat_timezones = await service.get_chat_timezones(chat_id=chat_id)
        if not chat_timezones:
            return

        time_match = TIME_RE.search(message.text)
        if time_match is None:
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

    @router.callback_query(F.data.regexp(UTC_CALLBACK_RE))
    async def set_user_utc(callback: CallbackQuery) -> None:
        if callback.data is None or callback.from_user is None or callback.message is None:
            return

        callback_match = UTC_CALLBACK_RE.match(callback.data)
        if callback_match is None:
            await callback.answer()
            return

        target_user_id = int(callback_match.group(1))
        selected_hour = int(callback_match.group(2))

        if callback.from_user.id != target_user_id:
            await callback.answer("Вы не можете выбрать UTC для другого пользователя.", show_alert=True)
            return

        sign = "+" if selected_hour >= 0 else ""
        timezone = f"UTC {sign}{selected_hour}"
        await service.set_user_timezone(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            chat_id=callback.message.chat.id,
            timezone=timezone,
        )

        await callback.answer("UTC сохранён")
        await callback.message.edit_reply_markup(reply_markup=None)

    return router
