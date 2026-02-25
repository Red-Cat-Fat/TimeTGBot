#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
EXAMPLE_ENV="$ROOT_DIR/example.env"
TARGET_ENV="$ROOT_DIR/.env"

if [ ! -f "$EXAMPLE_ENV" ]; then
  echo "Ошибка: не найден $EXAMPLE_ENV"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Ошибка: Docker не найден. Установите Docker и повторите попытку."
  exit 1
fi

echo "Шаг 1/4: Копирую шаблон переменных окружения..."
cp "$EXAMPLE_ENV" "$TARGET_ENV"

default_database_url=$(awk -F= '/^DATABASE_URL=/{print substr($0, index($0, "=")+1)}' "$EXAMPLE_ENV")

printf "Введите BOT_TOKEN (обязательно): "
IFS= read -r bot_token
while [ -z "$bot_token" ]; do
  printf "BOT_TOKEN не может быть пустым. Введите BOT_TOKEN: "
  IFS= read -r bot_token
done

printf "Введите DATABASE_URL (Enter для значения по умолчанию: %s): " "$default_database_url"
IFS= read -r database_url
if [ -z "$database_url" ]; then
  database_url="$default_database_url"
fi

echo "Шаг 2/4: Записываю переменные в .env..."
awk -v bot_token="$bot_token" -v database_url="$database_url" '
BEGIN { FS=OFS="=" }
$1 == "BOT_TOKEN" { $2 = bot_token; print; next }
$1 == "DATABASE_URL" { $2 = database_url; print; next }
{ print }
' "$TARGET_ENV" > "$TARGET_ENV.tmp"
mv "$TARGET_ENV.tmp" "$TARGET_ENV"

echo "Шаг 3/4: Собираю и запускаю контейнер..."
docker compose up --build

echo "Шаг 4/4: Готово."
