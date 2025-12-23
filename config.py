"""
Конфиг проекта

тут лежит все, что может понадобиться боту:
- токен
- список админов
- строка подключения к БД
- какие чаты бот периодически чистит
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(env_name: str) -> list[int]:

    raw = os.getenv(env_name, "")
    result: list[int] = []

    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            result.append(int(chunk))
        except ValueError:
            print(f"[config] предупреждение: в переменной {env_name} встретилось странное значение: {chunk!r}")

    return result


# токен бота

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise SystemExit("[config] Не задан BOT_TOKEN в .env, боту нечем авторизоваться(")


# админы бота

ADMIN_IDS: list[int] = _parse_ids("ADMIN_IDS")

if not ADMIN_IDS:
    print("[config] предупреждение: ADMIN_IDS пустой. Админов сейчас нет")


# база данных

# здесь лежит URL до бд
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./bot_data.db",
)


# чаты, которые бот чистит по расписанию

MODERATED_CHAT_IDS: list[int] = _parse_ids("MODERATED_CHAT_IDS")

if not MODERATED_CHAT_IDS:
    print("[config] инфо: MODERATED_CHAT_IDS пустой, периодическая проверка чатов выключена")