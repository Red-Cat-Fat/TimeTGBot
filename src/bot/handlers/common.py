from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import Message

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")


def create_common_router() -> Router:
    router = Router()

    @router.message(F.chat.type == "private")
    async def echo_message(message: Message) -> None:
        if message.text and TIME_RE.search(message.text):
            return

        await message.answer("Пока умею команды /start, /set_my_time и /help")

    return router
