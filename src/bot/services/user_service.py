from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)

    async def register_user(self, telegram_id: int, username: str | None) -> None:
        await self._users.get_or_create_user(telegram_id=telegram_id, username=username)
