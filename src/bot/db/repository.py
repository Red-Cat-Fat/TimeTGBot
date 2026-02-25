from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, UserChat


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            self._session.add(user)
            await self._session.flush()
            return user

        if user.username != username:
            user.username = username

        return user

    async def _get_or_create_user_chat(self, user_id: int, chat_id: int) -> UserChat:
        query = select(UserChat).where(UserChat.user_id == user_id, UserChat.chat_id == chat_id)
        result = await self._session.execute(query)
        user_chat = result.scalar_one_or_none()
        if user_chat is None:
            user_chat = UserChat(user_id=user_id, chat_id=chat_id)
            self._session.add(user_chat)
            await self._session.flush()

        return user_chat

    async def register_user_in_chat(self, telegram_id: int, username: str | None, chat_id: int) -> None:
        user = await self._get_or_create_user(telegram_id=telegram_id, username=username)
        await self._get_or_create_user_chat(user_id=user.id, chat_id=chat_id)
        await self._session.commit()

    async def set_user_chat_timezone(
        self,
        telegram_id: int,
        username: str | None,
        chat_id: int,
        timezone: str,
    ) -> None:
        user = await self._get_or_create_user(telegram_id=telegram_id, username=username)
        user_chat = await self._get_or_create_user_chat(user_id=user.id, chat_id=chat_id)
        user_chat.timezone = timezone
        await self._session.commit()

    async def get_user_timezone(self, telegram_id: int, chat_id: int) -> str | None:
        query = (
            select(UserChat.timezone)
            .join(User, User.id == UserChat.user_id)
            .where(User.telegram_id == telegram_id, UserChat.chat_id == chat_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_timezones(self, chat_id: int) -> list[str]:
        query = select(UserChat.timezone).where(UserChat.chat_id == chat_id, UserChat.timezone.is_not(None)).distinct()
        result = await self._session.execute(query)
        return [timezone for timezone in result.scalars().all() if timezone is not None]
