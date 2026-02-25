from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

UTC_MIN_OFFSET = -12
UTC_MAX_OFFSET = 14
SET_MY_TIME_CALLBACK_PREFIX = "set_my_time:set_utc"


def build_utc_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for hour in range(UTC_MIN_OFFSET, UTC_MAX_OFFSET + 1):
        sign = "+" if hour >= 0 else ""
        row.append(
            InlineKeyboardButton(
                text=f"UTC {sign}{hour}",
                callback_data=f"{SET_MY_TIME_CALLBACK_PREFIX}:{hour:+d}",
            )
        )
        if len(row) == 4:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_commands_router() -> Router:
    router = Router()

    @router.message(Command("set_my_time"))
    async def set_my_time_handler(message: Message) -> None:
        await message.answer(
            "Выберите ваш UTC:",
            reply_markup=build_utc_keyboard(),
        )

    return router
