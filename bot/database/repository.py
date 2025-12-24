"""
Repository-слой, который общается с бд
"""

from __future__ import annotations

from typing import List

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from .connection import SessionFactory
from .models import BlacklistedUser, ModerationLog, ModeratedChat


class UserRepository:
    def __init__(self, session_factory=SessionFactory):
        self._session_factory = session_factory

    # черный список

    async def add_to_blacklist(self, user_id: int, username: str | None = None) -> bool:
        async with self._session_factory() as session:
            try:
                res = await session.execute(
                    select(BlacklistedUser).where(BlacklistedUser.telegram_id == user_id)
                )
                existing = res.scalar_one_or_none()
                if existing:
                    return False

                session.add(BlacklistedUser(telegram_id=user_id, username=username))
                session.add(
                    ModerationLog(action="add", telegram_id=user_id, details=None)
                )
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def remove_from_blacklist(self, user_id: int) -> bool:
        async with self._session_factory() as session:
            try:
                res = await session.execute(
                    select(BlacklistedUser).where(BlacklistedUser.telegram_id == user_id)
                )
                user = res.scalar_one_or_none()
                if user is None:
                    return False

                await session.delete(user)
                session.add(
                    ModerationLog(action="remove", telegram_id=user_id, details=None)
                )
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def get_stats(self) -> dict:
        async with self._session_factory() as session:
            total_blacklisted = await session.scalar(
                select(func.count(BlacklistedUser.id))
            )
            total_actions = await session.scalar(
                select(func.count(ModerationLog.id))
            )
            last = await session.execute(
                select(ModerationLog)
                .order_by(ModerationLog.created_at.desc())
                .limit(1)
            )
            last_log = last.scalar_one_or_none()
            last_action = None
            if last_log is not None:
                last_action = f"{last_log.action} (user_id={last_log.telegram_id})"

            return {
                "blacklist_count": int(total_blacklisted or 0),
                "total_actions": int(total_actions or 0),
                "last_action": last_action,
            }

    async def run_check_for_chat(self, chat_id: int) -> List[int]:
        """
        Проверка чата по черному списку
        """
        async with self._session_factory() as session:
            res = await session.execute(select(BlacklistedUser.telegram_id))
            ids = [row[0] for row in res.all()]

            session.add(
                ModerationLog(
                    action="check_chat",
                    telegram_id=None,
                    chat_id=chat_id,
                    details=f"checked {len(ids)} users",
                )
            )
            await session.commit()

        return ids

    # чаты под модерацией

    async def add_moderated_chat(self, chat_id: int, title: str | None = None) -> bool:
        async with self._session_factory() as session:
            res = await session.execute(
                select(ModeratedChat).where(ModeratedChat.chat_id == chat_id)
            )
            existing = res.scalar_one_or_none()
            if existing:
                return False

            session.add(ModeratedChat(chat_id=chat_id, title=title))
            await session.commit()
            return True

    async def remove_moderated_chat(self, chat_id: int) -> bool:
        async with self._session_factory() as session:
            res = await session.execute(
                select(ModeratedChat).where(ModeratedChat.chat_id == chat_id)
            )
            existing = res.scalar_one_or_none()
            if existing is None:
                return False

            await session.delete(existing)
            await session.commit()
            return True

    async def get_moderated_chats(self) -> list[int]:
        async with self._session_factory() as session:
            res = await session.execute(select(ModeratedChat.chat_id))
            return [row[0] for row in res.all()]


# один общий репозиторий, которым пользуются хендлеры
user_repo = UserRepository()