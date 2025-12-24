# config.py
from __future__ import annotations

import logging
import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("config")
logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    # токен бота
    bot_token: str = Field(..., env="BOT_TOKEN")

    # параметры БД (значения по умолчанию такие же, как в docker-compose)
    db_name: str = Field("dashabot", env="POSTGRES_DB")
    db_user: str = Field("dashabot", env="POSTGRES_USER")
    db_password: str = Field("dashabot", env="POSTGRES_PASSWORD")
    db_host: str = Field("db", env="POSTGRES_HOST")
    db_port: int = Field(5432, env="POSTGRES_PORT")

    # «сырые» значения списков из окружения
    admin_ids_raw: Optional[str] = Field(default=None, env="ADMIN_IDS")
    moderated_chat_ids_raw: Optional[str] = Field(default=None, env="MODERATED_CHAT_IDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()


def _parse_int_list(raw: Optional[str]) -> List[int]:
    """
    Превращаем строку вида "1,2, 3" в [1, 2, 3].
    Если ничего нет или все битое – возвращаем пустой список.
    """
    if not raw:
        return []

    result: List[int] = []
    for chunk in raw.replace(" ", "").split(","):
        if not chunk:
            continue
        try:
            result.append(int(chunk))
        except ValueError:
            logger.warning("[config] не удалось разобрать '%s' как int в списке", chunk)
    return result


# ==== экспортируемые значения, которые используют хендлеры/БД ====

BOT_TOKEN: str = settings.bot_token
DATABASE_URL: str = settings.database_url

# Сначала берем из pydantic (он уже прочитал .env), если вдруг пусто – напрямую из os.environ
ADMIN_IDS: List[int] = _parse_int_list(settings.admin_ids_raw or os.getenv("ADMIN_IDS"))
MODERATED_CHAT_IDS: List[int] = _parse_int_list(
    settings.moderated_chat_ids_raw or os.getenv("MODERATED_CHAT_IDS")
)

if not ADMIN_IDS:
    logger.info("[config] предупреждение: ADMIN_IDS пустой, команды админов будут недоступны")
else:
    logger.info("[config] ADMIN_IDS = %s", ADMIN_IDS)

if not MODERATED_CHAT_IDS:
    logger.info(
        "[config] инфо: MODERATED_CHAT_IDS пустой, периодическая проверка чатов выключена"
    )
else:
    logger.info("[config] MODERATED_CHAT_IDS = %s", MODERATED_CHAT_IDS)