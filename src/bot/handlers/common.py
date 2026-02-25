from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import Message

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")


def create_common_router() -> Router:
    router = Router()

    @router.message(F.text & ~F.text.regexp(TIME_RE))
    async def echo_message(message: Message) -> None:
        await message.answer("Пока умею только команду /start")

    return router
