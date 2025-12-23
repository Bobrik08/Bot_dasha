"""
ORM-модели для нормальной бд
Здесь описываем таблицы, с которыми работает бот
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, DateTime, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class BlacklistedUser(Base):
    """
    Пользователь, который попал в черный список
    """
    __tablename__ = "blacklisted_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class ModerationLog(Base):
    """
    Простой лог действий модерации:
    - что сделали (add/remove/check_chat),
    - над кем и в каком чате
    """
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class ModeratedChat(Base):
    """
    Чаты, которые бот должен чистить по расписанию.
    """
    __tablename__ = "moderated_chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )