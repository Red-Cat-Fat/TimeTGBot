from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import ChatUserTimezone


class TimezoneRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def set_user_timezone(self, chat_id: int, user_id: int, offset: int) -> None:
        dialect_name = self._session.bind.dialect.name if self._session.bind is not None else ""

        if dialect_name == "sqlite":
            statement = sqlite_insert(ChatUserTimezone).values(
                chat_id=chat_id,
                user_id=user_id,
                utc_offset_minutes=offset,
            )
            statement = statement.on_conflict_do_update(
                index_elements=[ChatUserTimezone.chat_id, ChatUserTimezone.user_id],
                set_={"utc_offset_minutes": offset},
            )
            await self._session.execute(statement)
        elif dialect_name == "postgresql":
            statement = pg_insert(ChatUserTimezone).values(
                chat_id=chat_id,
                user_id=user_id,
                utc_offset_minutes=offset,
            )
            statement = statement.on_conflict_do_update(
                index_elements=[ChatUserTimezone.chat_id, ChatUserTimezone.user_id],
                set_={"utc_offset_minutes": offset},
            )
            await self._session.execute(statement)
        else:
            query = select(ChatUserTimezone).where(
                ChatUserTimezone.chat_id == chat_id,
                ChatUserTimezone.user_id == user_id,
            )
            result = await self._session.execute(query)
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    ChatUserTimezone(
                        chat_id=chat_id,
                        user_id=user_id,
                        utc_offset_minutes=offset,
                    )
                )
            else:
                row.utc_offset_minutes = offset

        await self._session.commit()

    async def get_user_timezone(self, chat_id: int, user_id: int) -> int | None:
        query = select(ChatUserTimezone.utc_offset_minutes).where(
            ChatUserTimezone.chat_id == chat_id,
            ChatUserTimezone.user_id == user_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_chat_timezones(self, chat_id: int) -> list[tuple[int, int]]:
        query = select(ChatUserTimezone.user_id, ChatUserTimezone.utc_offset_minutes).where(
            ChatUserTimezone.chat_id == chat_id
        )
        result = await self._session.execute(query)
        return [(user_id, offset) for user_id, offset in result.all()]
