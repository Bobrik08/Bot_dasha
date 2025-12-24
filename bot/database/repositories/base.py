"""
Базовый репозиторий.

Содержит базовый класс для всех репозиториев,
реализующий общие методы работы с БД.
"""

from typing import Generic, TypeVar, Type, Optional
from abc import ABC

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Базовый репозиторий для работы с моделями БД."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        """Инициализация репозитория.
        
        Args:
            session: Сессия базы данных
            model: Класс модели SQLAlchemy
        """
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID.
        
        Args:
            id: Идентификатор записи
            
        Returns:
            Модель или None, если не найдена
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> list[ModelType]:
        """Получить все записи.
        
        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            Список моделей
        """
        query = select(self.model).offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись.
        
        Args:
            **kwargs: Поля для создания записи
            
        Returns:
            Созданная модель
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись.
        
        Args:
            id: Идентификатор записи
            **kwargs: Поля для обновления
            
        Returns:
            Обновленная модель или None, если не найдена
        """
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """Удалить запись.
        
        Args:
            id: Идентификатор записи
            
        Returns:
            True, если запись была удалена, False если не найдена
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0

