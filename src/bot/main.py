from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import Settings
from bot.db.session import create_engine, create_session_factory, init_db
from bot.handlers.common import create_common_router
from bot.handlers.messages import create_messages_router
from bot.handlers.start import create_start_router


async def run() -> None:
    settings = Settings.from_env()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    await init_db(engine)

    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(create_start_router(session_factory))
    dispatcher.include_router(create_messages_router(session_factory))
    dispatcher.include_router(create_common_router())

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
