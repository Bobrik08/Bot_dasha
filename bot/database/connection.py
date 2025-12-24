"""
Подключение к базе данных.

Содержит функции для создания и управления подключением к БД.
Используется асинхронный режим SQLAlchemy.

Важно:
- Для "боевого" кода есть класс Database и объект db.
- Для старого кода и тестов оставлен совместимый интерфейс engine + SessionFactory.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from config import DATABASE_URL
from bot.database.models import Base


class Database:
    """Класс для управления подключением к базе данных"""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def initialize(self, url: str | None = None) -> None:
        """
        Инициализировать подключение к базе данных
        """
        db_url = url or DATABASE_URL

        self.engine = create_async_engine(
            db_url,
            echo=False,
            poolclass=NullPool,
            future=True,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def close(self) -> None:
        """Закрыть подключение к базе данных"""
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получить сессию БД.

        Пример:
            async with db.get_session() as session:
                ...
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call db.initialize() first.")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_tables(self) -> None:
        """Создать все таблицы в базе данных"""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call db.initialize() first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# Глобальный объект БД
db = Database()

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# совместимость с main.py: инициализация БД при старте бота
async def init_db() -> None:
    """
    Инициализация БД для старта бота.
    Сейчас engine/SessionFactory создаются при импорте модуля,
    поэтому здесь достаточно заглушки. При желании сюда можно
    добавить создание таблиц через Base.metadata.create_all.
    """
    return None