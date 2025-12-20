"""
Устаревший файл - используйте репозитории из bot.database.repositories.

Этот файл оставлен для обратной совместимости.
Новые функции должны использовать репозитории.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.connection import db
from bot.database.repositories import UserRepository


async def get_user(telegram_id: int) -> Optional:
    """Получить пользователя по Telegram ID.
    
    Args:
        telegram_id: Telegram ID пользователя
        
    Returns:
        Пользователь или None
    """
    async with db.get_session() as session:
        repo = UserRepository(session)
        return await repo.get_by_telegram_id(telegram_id)


async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
):
    """Получить пользователя или создать нового.
    
    Args:
        telegram_id: Telegram ID пользователя
        username: Имя пользователя
        first_name: Имя
        last_name: Фамилия
        
    Returns:
        Пользователь (существующий или новый)
    """
    async with db.get_session() as session:
        repo = UserRepository(session)
        return await repo.get_or_create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
