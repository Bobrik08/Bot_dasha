"""
Репозиторий для работы с пользователями.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория пользователей.
        
        Args:
            session: Сессия базы данных
        """
        super().__init__(session, User)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID.
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Пользователь или None, если не найден
        """
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Получить пользователя или создать нового.
        
        Args:
            telegram_id: Telegram ID пользователя
            username: Имя пользователя
            first_name: Имя
            last_name: Фамилия
            
        Returns:
            Пользователь (существующий или новый)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Обновляем данные, если они изменились
            update_data = {}
            if username is not None and user.username != username:
                update_data["username"] = username
            if first_name is not None and user.first_name != first_name:
                update_data["first_name"] = first_name
            if last_name is not None and user.last_name != last_name:
                update_data["last_name"] = last_name
            
            if update_data:
                user = await self.update(user.id, **update_data)
            return user
        
        return await self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
    
    async def get_active_users(self) -> list[User]:
        """Получить список активных пользователей.
        
        Returns:
            Список активных пользователей
        """
        result = await self.session.execute(
            select(User).where(User.is_active == True)
        )
        return list(result.scalars().all())
    
    async def get_admins(self) -> list[User]:
        """Получить список администраторов.
        
        Returns:
            Список администраторов
        """
        result = await self.session.execute(
            select(User).where(User.is_admin == True)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Получить количество пользователей.
        
        Returns:
            Количество пользователей
        """
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar() or 0

