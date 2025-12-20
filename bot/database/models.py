"""
Модели базы данных.

Содержит SQLAlchemy модели для всех таблиц БД.
Используется асинхронный режим SQLAlchemy.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class User(Base):
    """Модель пользователя бота."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Связи
    allowed_users: Mapped[list["AllowedUser"]] = relationship(
        "AllowedUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    group_members: Mapped[list["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Group(Base):
    """Модель группы Telegram."""
    
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Связи
    allowed_users: Mapped[list["AllowedUser"]] = relationship(
        "AllowedUser",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    members: Mapped[list["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Строковое представление группы."""
        return f"<Group(telegram_id={self.telegram_id}, title={self.title})>"


class AllowedUser(Base):
    """Модель разрешенного пользователя в группе.
    
    Связывает пользователя и группу, определяя, что пользователь
    разрешен для нахождения в данной группе.
    """
    
    __tablename__ = "allowed_users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    added_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Связи
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="allowed_users")
    group: Mapped["Group"] = relationship("Group", back_populates="allowed_users")
    
    # Уникальный индекс для пары user_id + group_id
    __table_args__ = (
        Index("idx_allowed_user_group", "user_id", "group_id", unique=True),
    )
    
    def __repr__(self) -> str:
        """Строковое представление разрешенного пользователя."""
        return f"<AllowedUser(user_id={self.user_id}, group_id={self.group_id})>"


class GroupMember(Base):
    """Модель участника группы.
    
    Хранит информацию о текущих участниках группы для отслеживания
    и сравнения с разрешенным списком.
    """
    
    __tablename__ = "group_members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="group_members")
    group: Mapped["Group"] = relationship("Group", back_populates="members")
    
    # Уникальный индекс для пары user_id + group_id
    __table_args__ = (
        Index("idx_member_user_group", "user_id", "group_id", unique=True),
    )
    
    def __repr__(self) -> str:
        """Строковое представление участника группы."""
        return f"<GroupMember(user_id={self.user_id}, group_id={self.group_id}, status={self.status})>"


class ActionLog(Base):
    """Модель лога действий бота."""
    
    __tablename__ = "action_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    target_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    def __repr__(self) -> str:
        """Строковое представление лога."""
        return f"<ActionLog(action_type={self.action_type}, created_at={self.created_at})>"
