from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    telegram_token: str
    database_url: str = "sqlite+aiosqlite:///./bot.db"

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN")
        if not token:
            msg = "Environment variable BOT_TOKEN is required"
            raise RuntimeError(msg)

        db_url = os.getenv("DATABASE_URL", cls.database_url)
        return cls(telegram_token=token, database_url=db_url)
