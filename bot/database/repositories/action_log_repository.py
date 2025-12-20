"""
Репозиторий для работы с логами действий.
"""

from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import ActionLog
from bot.database.repositories.base import BaseRepository


class ActionLogRepository(BaseRepository[ActionLog]):
    """Репозиторий для работы с логами действий."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория логов действий.
        
        Args:
            session: Сессия базы данных
        """
        super().__init__(session, ActionLog)
    
    async def create_log(
        self,
        action_type: str,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        details: Optional[str] = None
    ) -> ActionLog:
        """Создать запись в логе.
        
        Args:
            action_type: Тип действия
            user_id: ID пользователя, выполнившего действие
            group_id: ID группы (если применимо)
            target_user_id: ID целевого пользователя (если применимо)
            details: Дополнительные детали
            
        Returns:
            Созданная запись лога
        """
        return await self.create(
            action_type=action_type,
            user_id=user_id,
            group_id=group_id,
            target_user_id=target_user_id,
            details=details
        )
    
    async def get_logs_by_action_type(
        self,
        action_type: str,
        limit: Optional[int] = None
    ) -> list[ActionLog]:
        """Получить логи по типу действия.
        
        Args:
            action_type: Тип действия
            limit: Максимальное количество записей
            
        Returns:
            Список логов
        """
        query = select(ActionLog).where(
            ActionLog.action_type == action_type
        ).order_by(desc(ActionLog.created_at))
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_logs_by_group(
        self,
        group_id: int,
        limit: Optional[int] = None
    ) -> list[ActionLog]:
        """Получить логи для группы.
        
        Args:
            group_id: ID группы
            limit: Максимальное количество записей
            
        Returns:
            Список логов
        """
        query = select(ActionLog).where(
            ActionLog.group_id == group_id
        ).order_by(desc(ActionLog.created_at))
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

