from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re

from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.db.repositories.timezones import TimezoneRepository

UTC_OFFSET_RE = re.compile(r"^\s*(?:UTC\s*)?([+-])\s*(\d{1,2})(?::?(\d{2}))?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class UtcOffset:
    raw: str
    delta: timedelta

    @property
    def label(self) -> str:
        total_minutes = int(self.delta.total_seconds() // 60)
        sign = "+" if total_minutes >= 0 else "-"
        abs_minutes = abs(total_minutes)
        hours, minutes = divmod(abs_minutes, 60)
        if minutes == 0:
            return f"UTC {sign}{hours}"
        return f"UTC {sign}{hours}:{minutes:02d}"


def parse_utc_offset(value: str) -> UtcOffset | None:
    match = UTC_OFFSET_RE.match(value)
    if not match:
        return None

    sign_raw, hours_raw, minutes_raw = match.groups()
    hours = int(hours_raw)
    minutes = int(minutes_raw or "0")
    if hours > 14 or minutes > 59:
        return None

    signed_minutes = hours * 60 + minutes
    if sign_raw == "-":
        signed_minutes *= -1

    return UtcOffset(raw=value, delta=timedelta(minutes=signed_minutes))


class TimeConversionService:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def get_sender_timezone(self, user_id: int, chat_id: int) -> UtcOffset | None:
        async with self._session_factory() as session:
            timezone_repository = TimezoneRepository(session)
            sender_offset = await timezone_repository.get_user_timezone(chat_id=chat_id, user_id=user_id)

        if sender_offset is None:
            return None

        return UtcOffset(
            raw=f"UTC {sender_offset // 60:+d}",
            delta=timedelta(minutes=sender_offset),
        )

    async def set_user_timezone(self, user_id: int, username: str | None, chat_id: int, timezone: str) -> None:
        del username
        parsed_timezone = parse_utc_offset(timezone)
        if parsed_timezone is None:
            return

        minutes = int(parsed_timezone.delta.total_seconds() // 60)
        async with self._session_factory() as session:
            timezone_repository = TimezoneRepository(session)
            await timezone_repository.set_user_timezone(
                chat_id=chat_id,
                user_id=user_id,
                offset=minutes,
            )

    async def get_chat_timezones(self, chat_id: int) -> list[UtcOffset]:
        async with self._session_factory() as session:
            timezone_repository = TimezoneRepository(session)
            rows = await timezone_repository.list_chat_timezones(chat_id=chat_id)

        seen: set[int] = set()
        offsets: list[UtcOffset] = []
        for _, offset_minutes in rows:
            key = offset_minutes * 60
            if key in seen:
                continue

            seen.add(key)
            offsets.append(
                UtcOffset(
                    raw=f"UTC {offset_minutes // 60:+d}",
                    delta=timedelta(minutes=offset_minutes),
                )
            )

        return sorted(offsets, key=lambda item: item.delta)

    def convert_time(self, source_time: str, sender_timezone: UtcOffset, target_timezone: UtcOffset) -> str:
        current_day = datetime.now().date()
        local_dt = datetime.strptime(source_time, "%H:%M").replace(
            year=current_day.year,
            month=current_day.month,
            day=current_day.day,
        )
        utc_dt = local_dt - sender_timezone.delta
        target_dt = utc_dt + target_timezone.delta
        return target_dt.strftime("%H:%M")
