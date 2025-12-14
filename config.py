import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str | None) -> List[int]:
    result: List[int] = []
    if not raw:
        return result

    parts = raw.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError:
            continue
    return result


@dataclass
class Config:
    bot_token: str
    database_url: str
    admin_ids: List[int]


config = Config(
    bot_token=os.getenv("BOT_TOKEN", ""),
    database_url=os.getenv("DATABASE_URL", ""),
    admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS")),
)


BOT_TOKEN = config.bot_token
DATABASE_URL = config.database_url
ADMIN_IDS = config.admin_ids

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Создай файл .env в корне проекта и добавь строку BOT_TOKEN=..."
    )

if not ADMIN_IDS:
    print("Внимание: ADMIN_IDS пустой, админ-команды работать не будут.")
