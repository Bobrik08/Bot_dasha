"""
Репозиторий для работы с разрешенными пользователями.
"""

from typing import Optional

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import AllowedUser, User, Group
from bot.database.repositories.base import BaseRepository


class AllowedUserRepository(BaseRepository[AllowedUser]):
    """Репозиторий для работы с разрешенными пользователями."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория разрешенных пользователей.
        
        Args:
            session: Сессия базы данных
        """
        super().__init__(session, AllowedUser)
    
    async def get_by_user_and_group(
        self,
        user_id: int,
        group_id: int
    ) -> Optional[AllowedUser]:
        """Получить разрешение для пользователя в группе.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            
        Returns:
            Разрешение или None, если не найдено
        """
        result = await self.session.execute(
            select(AllowedUser).where(
                and_(
                    AllowedUser.user_id == user_id,
                    AllowedUser.group_id == group_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def is_allowed(self, user_id: int, group_id: int) -> bool:
        """Проверить, разрешен ли пользователь в группе.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            
        Returns:
            True, если пользователь разрешен, False иначе
        """
        allowed = await self.get_by_user_and_group(user_id, group_id)
        return allowed is not None
    
    async def add_allowed_user(
        self,
        user_id: int,
        group_id: int,
        added_by: Optional[int] = None
    ) -> AllowedUser:
        """Добавить разрешенного пользователя в группу.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            added_by: ID пользователя, который добавил
            
        Returns:
            Созданное разрешение
        """
        existing = await self.get_by_user_and_group(user_id, group_id)
        if existing:
            return existing
        
        return await self.create(
            user_id=user_id,
            group_id=group_id,
            added_by=added_by
        )
    
    async def remove_allowed_user(self, user_id: int, group_id: int) -> bool:
        """Удалить разрешение пользователя в группе.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            
        Returns:
            True, если разрешение было удалено, False если не найдено
        """
        result = await self.session.execute(
            delete(AllowedUser).where(
                and_(
                    AllowedUser.user_id == user_id,
                    AllowedUser.group_id == group_id
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_allowed_users_for_group(self, group_id: int) -> list[User]:
        """Получить список разрешенных пользователей для группы.
        
        Args:
            group_id: ID группы
            
        Returns:
            Список разрешенных пользователей
        """
        result = await self.session.execute(
            select(User).join(AllowedUser).where(
                AllowedUser.group_id == group_id
            )
        )
        return list(result.scalars().all())
    
    async def get_allowed_telegram_ids_for_group(self, group_id: int) -> list[int]:
        """Получить список Telegram ID разрешенных пользователей для группы.
        
        Args:
            group_id: ID группы
            
        Returns:
            Список Telegram ID разрешенных пользователей
        """
        result = await self.session.execute(
            select(User.telegram_id).join(AllowedUser).where(
                AllowedUser.group_id == group_id
            )
        )
        return list(result.scalars().all())

