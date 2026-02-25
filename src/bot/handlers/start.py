from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.services.user_service import UserService


def create_start_router(session_factory: async_sessionmaker) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start_handler(message: Message) -> None:
        if message.from_user is None:
            return

        async with session_factory() as session:
            service = UserService(session)
            await service.register_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                chat_id=message.chat.id,
            )

        await message.answer("Привет! Я готов работать 🚀")

    return router
