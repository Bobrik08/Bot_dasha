"""
Репозиторий для работы с участниками групп.
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import GroupMember, User, Group
from bot.database.repositories.base import BaseRepository


class GroupMemberRepository(BaseRepository[GroupMember]):
    """Репозиторий для работы с участниками групп."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория участников групп.
        
        Args:
            session: Сессия базы данных
        """
        super().__init__(session, GroupMember)
    
    async def get_by_user_and_group(
        self,
        user_id: int,
        group_id: int
    ) -> Optional[GroupMember]:
        """Получить участника группы.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            
        Returns:
            Участник группы или None, если не найден
        """
        result = await self.session.execute(
            select(GroupMember).where(
                and_(
                    GroupMember.user_id == user_id,
                    GroupMember.group_id == group_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def add_member(
        self,
        user_id: int,
        group_id: int,
        status: str = "member"
    ) -> GroupMember:
        """Добавить участника в группу.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            status: Статус участника
            
        Returns:
            Созданный участник группы
        """
        existing = await self.get_by_user_and_group(user_id, group_id)
        if existing:
            # Обновляем статус и время последнего визита
            await self.update(
                existing.id,
                status=status,
                last_seen=datetime.utcnow()
            )
            await self.session.refresh(existing)
            return existing
        
        return await self.create(
            user_id=user_id,
            group_id=group_id,
            status=status,
            joined_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
    
    async def remove_member(self, user_id: int, group_id: int) -> bool:
        """Удалить участника из группы.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
            
        Returns:
            True, если участник был удален, False если не найден
        """
        result = await self.session.execute(
            delete(GroupMember).where(
                and_(
                    GroupMember.user_id == user_id,
                    GroupMember.group_id == group_id
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_members_for_group(self, group_id: int) -> list[User]:
        """Получить список участников группы.
        
        Args:
            group_id: ID группы
            
        Returns:
            Список участников группы
        """
        result = await self.session.execute(
            select(User).join(GroupMember).where(
                GroupMember.group_id == group_id
            )
        )
        return list(result.scalars().all())
    
    async def get_member_telegram_ids_for_group(self, group_id: int) -> list[int]:
        """Получить список Telegram ID участников группы.
        
        Args:
            group_id: ID группы
            
        Returns:
            Список Telegram ID участников группы
        """
        result = await self.session.execute(
            select(User.telegram_id).join(GroupMember).where(
                GroupMember.group_id == group_id
            )
        )
        return list(result.scalars().all())
    
    async def update_last_seen(self, user_id: int, group_id: int) -> None:
        """Обновить время последнего визита участника.
        
        Args:
            user_id: ID пользователя
            group_id: ID группы
        """
        member = await self.get_by_user_and_group(user_id, group_id)
        if member:
            await self.update(member.id, last_seen=datetime.utcnow())

