from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message


def create_common_router() -> Router:
    router = Router()

    @router.message(F.text)
    async def echo_message(message: Message) -> None:
        await message.answer("Пока умею только команду /start")

    return router
