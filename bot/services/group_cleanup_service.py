"""
Сервис для очистки групп от неразрешенных пользователей.

Реализует основную бизнес-логику бота:
- Получение списка участников группы
- Сравнение с разрешенным списком
- Удаление неразрешенных пользователей
"""

from typing import List, Set
from logging import getLogger

from aiogram import Bot
from aiogram.types import ChatMember

from bot.database.connection import db
from bot.database.repositories import (
    UserRepository,
    GroupRepository,
    AllowedUserRepository,
    GroupMemberRepository,
    ActionLogRepository
)

logger = getLogger(__name__)


class GroupCleanupService:
    """Сервис для очистки групп от неразрешенных пользователей."""
    
    def __init__(self, bot: Bot) -> None:
        """Инициализация сервиса.
        
        Args:
            bot: Экземпляр бота для работы с Telegram API
        """
        self.bot = bot
    
    async def cleanup_group(self, group_telegram_id: int) -> dict:
        """Очистить группу от неразрешенных пользователей.
        
        Args:
            group_telegram_id: Telegram ID группы
            
        Returns:
            Словарь с результатами очистки:
            - removed_count: количество удаленных пользователей
            - errors: список ошибок
            - removed_users: список удаленных пользователей
        """
        result = {
            "removed_count": 0,
            "errors": [],
            "removed_users": []
        }
        
        try:
            async with db.get_session() as session:
                # Получаем репозитории
                group_repo = GroupRepository(session)
                user_repo = UserRepository(session)
                allowed_repo = AllowedUserRepository(session)
                member_repo = GroupMemberRepository(session)
                log_repo = ActionLogRepository(session)
                
                # Получаем или создаем группу в БД
                group = await group_repo.get_by_telegram_id(group_telegram_id)
                if not group:
                    chat = await self.bot.get_chat(group_telegram_id)
                    group = await group_repo.get_or_create(
                        telegram_id=group_telegram_id,
                        title=chat.title,
                        username=chat.username
                    )
                
                # Получаем список участников группы из Telegram
                members = await self._get_group_members(group_telegram_id)
                
                # Получаем список разрешенных пользователей из БД
                allowed_telegram_ids = await allowed_repo.get_allowed_telegram_ids_for_group(
                    group.id
                )
                allowed_set = set(allowed_telegram_ids)
                
                # Обновляем информацию об участниках в БД
                for member in members:
                    if member.user.is_bot:
                        continue
                    
                    user = await user_repo.get_or_create(
                        telegram_id=member.user.id,
                        username=member.user.username,
                        first_name=member.user.first_name,
                        last_name=member.user.last_name
                    )
                    
                    await member_repo.add_member(
                        user_id=user.id,
                        group_id=group.id,
                        status=member.status
                    )
                
                # Находим пользователей для удаления
                members_to_remove = [
                    member for member in members
                    if not member.user.is_bot
                    and member.user.id not in allowed_set
                    and member.status not in ["creator", "administrator"]
                ]
                
                # Удаляем неразрешенных пользователей
                for member in members_to_remove:
                    try:
                        await self.bot.ban_chat_member(
                            chat_id=group_telegram_id,
                            user_id=member.user.id
                        )
                        
                        result["removed_count"] += 1
                        result["removed_users"].append({
                            "telegram_id": member.user.id,
                            "username": member.user.username,
                            "first_name": member.user.first_name
                        })
                        
                        # Удаляем из БД
                        user = await user_repo.get_by_telegram_id(member.user.id)
                        if user:
                            await member_repo.remove_member(user.id, group.id)
                        
                        # Логируем действие
                        await log_repo.create_log(
                            action_type="user_removed",
                            group_id=group.id,
                            target_user_id=user.id if user else None,
                            details=f"User {member.user.id} removed from group {group_telegram_id}"
                        )
                        
                        logger.info(
                            f"Removed user {member.user.id} from group {group_telegram_id}"
                        )
                    
                    except Exception as e:
                        error_msg = f"Failed to remove user {member.user.id}: {str(e)}"
                        result["errors"].append(error_msg)
                        logger.error(error_msg)
                
                # Логируем общее действие
                await log_repo.create_log(
                    action_type="group_cleanup",
                    group_id=group.id,
                    details=f"Cleaned group {group_telegram_id}, removed {result['removed_count']} users"
                )
        
        except Exception as e:
            error_msg = f"Error during group cleanup: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg, exc_info=True)
        
        return result
    
    async def _get_group_members(self, group_telegram_id: int) -> List[ChatMember]:
        """Получить список участников группы.
        
        Args:
            group_telegram_id: Telegram ID группы
            
        Returns:
            Список участников группы
        """
        members = []
        try:
            # Получаем администраторов группы
            administrators = await self.bot.get_chat_administrators(group_telegram_id)
            members.extend(administrators)
            
            # Для получения всех участников нужно использовать другой метод
            # В Telegram Bot API нет прямого метода для получения всех участников
            # Поэтому мы работаем только с администраторами и теми, кого видим
            
        except Exception as e:
            logger.error(f"Error getting group members: {str(e)}", exc_info=True)
        
        return members
    
    async def add_allowed_user(
        self,
        group_telegram_id: int,
        user_telegram_id: int,
        added_by_telegram_id: int
    ) -> bool:
        """Добавить пользователя в список разрешенных для группы.
        
        Args:
            group_telegram_id: Telegram ID группы
            user_telegram_id: Telegram ID пользователя
            added_by_telegram_id: Telegram ID пользователя, который добавил
            
        Returns:
            True, если пользователь был добавлен, False иначе
        """
        try:
            async with db.get_session() as session:
                group_repo = GroupRepository(session)
                user_repo = UserRepository(session)
                allowed_repo = AllowedUserRepository(session)
                log_repo = ActionLogRepository(session)
                
                # Получаем или создаем группу
                group = await group_repo.get_by_telegram_id(group_telegram_id)
                if not group:
                    chat = await self.bot.get_chat(group_telegram_id)
                    group = await group_repo.get_or_create(
                        telegram_id=group_telegram_id,
                        title=chat.title,
                        username=chat.username
                    )
                
                # Получаем или создаем пользователя
                user = await user_repo.get_or_create(telegram_id=user_telegram_id)
                
                # Получаем пользователя, который добавил
                added_by = await user_repo.get_by_telegram_id(added_by_telegram_id)
                
                # Добавляем в разрешенные
                await allowed_repo.add_allowed_user(
                    user_id=user.id,
                    group_id=group.id,
                    added_by=added_by.id if added_by else None
                )
                
                # Логируем действие
                await log_repo.create_log(
                    action_type="user_allowed",
                    user_id=added_by.id if added_by else None,
                    group_id=group.id,
                    target_user_id=user.id,
                    details=f"User {user_telegram_id} added to allowed list for group {group_telegram_id}"
                )
                
                return True
        
        except Exception as e:
            logger.error(f"Error adding allowed user: {str(e)}", exc_info=True)
            return False
    
    async def remove_allowed_user(
        self,
        group_telegram_id: int,
        user_telegram_id: int
    ) -> bool:
        """Удалить пользователя из списка разрешенных для группы.
        
        Args:
            group_telegram_id: Telegram ID группы
            user_telegram_id: Telegram ID пользователя
            
        Returns:
            True, если пользователь был удален, False иначе
        """
        try:
            async with db.get_session() as session:
                group_repo = GroupRepository(session)
                user_repo = UserRepository(session)
                allowed_repo = AllowedUserRepository(session)
                log_repo = ActionLogRepository(session)
                
                # Получаем группу
                group = await group_repo.get_by_telegram_id(group_telegram_id)
                if not group:
                    return False
                
                # Получаем пользователя
                user = await user_repo.get_by_telegram_id(user_telegram_id)
                if not user:
                    return False
                
                # Удаляем из разрешенных
                removed = await allowed_repo.remove_allowed_user(user.id, group.id)
                
                if removed:
                    # Логируем действие
                    await log_repo.create_log(
                        action_type="user_disallowed",
                        group_id=group.id,
                        target_user_id=user.id,
                        details=f"User {user_telegram_id} removed from allowed list for group {group_telegram_id}"
                    )
                
                return removed
        
        except Exception as e:
            logger.error(f"Error removing allowed user: {str(e)}", exc_info=True)
            return False

