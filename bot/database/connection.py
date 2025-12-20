"""
Подключение к базе данных.

Содержит функции для создания и управления подключением к БД.
Используется асинхронный режим SQLAlchemy.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

from config import settings
from bot.database.models import Base


class Database:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self) -> None:
        """Инициализация подключения к БД."""
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
    
    def initialize(self) -> None:
        """Инициализация подключения к базе данных."""
        database_url = (
            f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Установить True для отладки SQL запросов
            poolclass=NullPool,  # Для асинхронных операций
            future=True
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
    
    async def close(self) -> None:
        """Закрытие подключения к базе данных."""
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение сессии БД.
        
        Yields:
            AsyncSession: Сессия базы данных
            
        Example:
            async with db.get_session() as session:
                # Работа с БД
                pass
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
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
        """Создание всех таблиц в базе данных."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# Глобальный экземпляр БД
db = Database()
