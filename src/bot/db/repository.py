from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(telegram_id=telegram_id, username=username)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
