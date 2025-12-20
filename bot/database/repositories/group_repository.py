"""
Репозиторий для работы с группами.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Group
from bot.database.repositories.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    """Репозиторий для работы с группами."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория групп.
        
        Args:
            session: Сессия базы данных
        """
        super().__init__(session, Group)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Group]:
        """Получить группу по Telegram ID.
        
        Args:
            telegram_id: Telegram ID группы
            
        Returns:
            Группа или None, если не найдена
        """
        result = await self.session.execute(
            select(Group).where(Group.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(
        self,
        telegram_id: int,
        title: Optional[str] = None,
        username: Optional[str] = None
    ) -> Group:
        """Получить группу или создать новую.
        
        Args:
            telegram_id: Telegram ID группы
            title: Название группы
            username: Username группы
            
        Returns:
            Группа (существующая или новая)
        """
        group = await self.get_by_telegram_id(telegram_id)
        if group:
            # Обновляем данные, если они изменились
            update_data = {}
            if title is not None and group.title != title:
                update_data["title"] = title
            if username is not None and group.username != username:
                update_data["username"] = username
            
            if update_data:
                group = await self.update(group.id, **update_data)
            return group
        
        return await self.create(
            telegram_id=telegram_id,
            title=title,
            username=username
        )
    
    async def get_active_groups(self) -> list[Group]:
        """Получить список активных групп.
        
        Returns:
            Список активных групп
        """
        result = await self.session.execute(
            select(Group).where(Group.is_active == True)
        )
        return list(result.scalars().all())

