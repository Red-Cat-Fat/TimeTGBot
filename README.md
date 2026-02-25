# TimeTGBot

Базовая структура Telegram-бота на `aiogram` с разделением на слои:

- `src/bot/main.py` — точка входа.
- `src/bot/handlers/` — обработчики команд и сообщений.
- `src/bot/services/` — бизнес-логика.
- `src/bot/db/` — модели и доступ к БД.
- `src/bot/config.py` — чтение переменных окружения.

## Требования

- Python 3.11+
- Telegram bot token

## Запуск локально

1. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Установите зависимости:

   ```bash
   pip install -U pip
   pip install .
   ```

3. Укажите переменные окружения:

   ```bash
   export BOT_TOKEN="<ваш_токен>"
   export DATABASE_URL="sqlite+aiosqlite:///./bot.db"
   ```

4. Запустите бота:

   ```bash
   python -m bot.main
   ```

## Запуск в Docker

1. Соберите образ:

   ```bash
   docker build -t time-tg-bot .
   ```

2. Запустите контейнер:

   ```bash
   docker run --rm \
     -e BOT_TOKEN="<ваш_токен>" \
     -e DATABASE_URL="sqlite+aiosqlite:///./bot.db" \
     time-tg-bot
   ```

## Запуск через docker-compose

1. Создайте `.env` рядом с `docker-compose.yml`:

   ```env
   BOT_TOKEN=<ваш_токен>
   ```

2. Запустите:

   ```bash
   docker compose up --build
   ```


## Миграции

В проекте добавлена SQL-миграция `migrations/001_create_chat_user_timezones.sql` для создания таблицы `chat_user_timezones` и уникального составного индекса `(chat_id, user_id)`.

Пример применения миграции для SQLite:

```bash
sqlite3 bot.db < migrations/001_create_chat_user_timezones.sql
```

### Схема `chat_user_timezones`

- `id` — первичный ключ.
- `chat_id` — ID чата Telegram.
- `user_id` — ID пользователя Telegram.
- `utc_offset_minutes` — смещение пользователя относительно UTC в минутах.
- `updated_at` — дата/время последнего обновления записи.
- `ux_chat_user_timezones_chat_id_user_id` — уникальный составной индекс для upsert по `(chat_id, user_id)`.
