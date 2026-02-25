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

echo "Шаг 1/5: Обновляю проект из Git..."
git -C "$ROOT_DIR" pull

default_database_url=$(awk -F= '/^DATABASE_URL=/{print substr($0, index($0, "=")+1)}' "$EXAMPLE_ENV")
current_bot_token=""
current_database_url=""

if [ -f "$TARGET_ENV" ]; then
  current_bot_token=$(awk -F= '/^BOT_TOKEN=/{print substr($0, index($0, "=")+1)}' "$TARGET_ENV")
  current_database_url=$(awk -F= '/^DATABASE_URL=/{print substr($0, index($0, "=")+1)}' "$TARGET_ENV")

  echo "Шаг 2/5: Найден существующий .env файл."
  printf "Обновить значения переменных? (y/N): "
  IFS= read -r should_update

  case "$should_update" in
    y|Y|yes|YES)
      ;;
    *)
      echo "Шаг 3/5: Использую существующий .env без изменений."
      echo "Шаг 4/5: Собираю и запускаю контейнер..."
      docker compose up --build
      echo "Шаг 5/5: Готово."
      exit 0
      ;;
  esac
else
  echo "Шаг 2/5: .env не найден, создаю из шаблона."
fi

echo "Шаг 3/5: Подготавливаю .env..."
cp "$EXAMPLE_ENV" "$TARGET_ENV"

if [ -n "$current_bot_token" ]; then
  printf "Введите BOT_TOKEN (Enter для текущего значения): "
else
  printf "Введите BOT_TOKEN (обязательно): "
fi
IFS= read -r bot_token
while [ -z "$bot_token" ]; do
  if [ -n "$current_bot_token" ]; then
    bot_token="$current_bot_token"
    break
  fi

  printf "BOT_TOKEN не может быть пустым. Введите BOT_TOKEN: "
  IFS= read -r bot_token
done

database_url_default="$default_database_url"
if [ -n "$current_database_url" ]; then
  database_url_default="$current_database_url"
fi

printf "Введите DATABASE_URL (Enter для значения по умолчанию: %s): " "$database_url_default"
IFS= read -r database_url
if [ -z "$database_url" ]; then
  database_url="$database_url_default"
fi

echo "Шаг 4/5: Записываю переменные в .env..."
awk -v bot_token="$bot_token" -v database_url="$database_url" '
BEGIN { FS=OFS="=" }
$1 == "BOT_TOKEN" { $2 = bot_token; print; next }
$1 == "DATABASE_URL" { $2 = database_url; print; next }
{ print }
' "$TARGET_ENV" > "$TARGET_ENV.tmp"
mv "$TARGET_ENV.tmp" "$TARGET_ENV"

echo "Шаг 5/5: Собираю и запускаю контейнер..."
docker compose up --build

echo "Готово."
