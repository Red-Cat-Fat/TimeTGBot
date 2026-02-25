from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)

    async def register_user(self, telegram_id: int, username: str | None, chat_id: int) -> None:
        await self._users.register_user_in_chat(telegram_id=telegram_id, username=username, chat_id=chat_id)

    async def set_user_timezone(
        self,
        telegram_id: int,
        username: str | None,
        chat_id: int,
        timezone: str,
    ) -> None:
        await self._users.set_user_chat_timezone(
            telegram_id=telegram_id,
            username=username,
            chat_id=chat_id,
            timezone=timezone,
        )

    async def get_user_timezone(self, telegram_id: int, chat_id: int) -> str | None:
        return await self._users.get_user_timezone(telegram_id=telegram_id, chat_id=chat_id)

    async def get_chat_timezones(self, chat_id: int) -> list[str]:
        return await self._users.get_chat_timezones(chat_id=chat_id)
