"""
Подключение к бд и async-сессии
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DATABASE_URL


# сам движок
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)

SessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_db() -> None:
    """
    Создаем таблицы, если их ещё нет
    """
    from .models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)