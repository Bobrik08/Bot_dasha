# Подробное объяснение кода проекта

Этот файл содержит построчные комментарии ко всем Python файлам, которые были написаны в проекте.

---

## 1. config.py - Конфигурация проекта

```python
"""
Конфигурация проекта.

Содержит настройки бота, базы данных и другие параметры.
Секреты загружаются из переменных окружения через .env файл.
"""
```
**Объяснение:** Docstring модуля - описание того, что делает этот файл. Здесь хранятся все настройки приложения.

```python
from pydantic_settings import BaseSettings
from pydantic import Field
```
**Объяснение:** 
- `BaseSettings` - базовый класс из библиотеки pydantic-settings для работы с настройками
- `Field` - используется для описания полей с валидацией и загрузкой из переменных окружения

```python
class Settings(BaseSettings):
    """Настройки приложения."""
```
**Объяснение:** Класс для хранения всех настроек. Наследуется от BaseSettings, что позволяет автоматически загружать значения из .env файла.

```python
    # Токен бота
    bot_token: str = Field(..., env="BOT_TOKEN", description="Токен Telegram бота")
```
**Объяснение:**
- `bot_token` - поле для хранения токена бота
- `str` - тип данных (строка)
- `Field(...)` - обязательное поле (три точки означают обязательность)
- `env="BOT_TOKEN"` - имя переменной окружения, из которой загружается значение
- `description` - описание поля для документации

```python
    # Настройки базы данных
    db_host: str = Field(default="localhost", env="DB_HOST", description="Хост БД")
    db_port: int = Field(default=5432, env="DB_PORT", description="Порт БД")
    db_name: str = Field(..., env="DB_NAME", description="Имя базы данных")
    db_user: str = Field(..., env="DB_USER", description="Пользователь БД")
    db_password: str = Field(..., env="DB_PASSWORD", description="Пароль БД")
```
**Объяснение:** Настройки подключения к базе данных PostgreSQL:
- `db_host` - адрес сервера БД (по умолчанию localhost)
- `db_port` - порт (по умолчанию 5432 - стандартный порт PostgreSQL)
- `db_name` - имя базы данных (обязательное поле)
- `db_user` - имя пользователя БД (обязательное поле)
- `db_password` - пароль БД (обязательное поле, секрет!)

```python
    # ID администраторов (строка через запятую, например: "123456789,987654321")
    admin_ids_str: str = Field(default="", env="ADMIN_IDS", description="Список ID администраторов через запятую")
```
**Объяснение:** Храним ID администраторов как строку, потому что в .env файле нельзя хранить списки напрямую. Формат: "123,456,789"

```python
    @property
    def admin_ids(self) -> list[int]:
        """Получить список ID администраторов."""
        if not self.admin_ids_str:
            return []
        return [int(id.strip()) for id in self.admin_ids_str.split(",") if id.strip()]
```
**Объяснение:**
- `@property` - декоратор, делает метод доступным как атрибут (можно писать `settings.admin_ids` вместо `settings.admin_ids()`)
- `-> list[int]` - тип возвращаемого значения (список целых чисел)
- `if not self.admin_ids_str` - если строка пустая, возвращаем пустой список
- `self.admin_ids_str.split(",")` - разбиваем строку по запятым
- `id.strip()` - убираем пробелы вокруг каждого ID
- `int(id.strip())` - преобразуем строку в число
- `if id.strip()` - пропускаем пустые значения

```python
    class Config:
        """Конфигурация Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```
**Объяснение:** Внутренний класс для настройки Pydantic:
- `env_file = ".env"` - имя файла с переменными окружения
- `env_file_encoding = "utf-8"` - кодировка файла
- `case_sensitive = False` - регистр не важен (BOT_TOKEN = bot_token)

```python
# Глобальный экземпляр настроек
settings = Settings()
```
**Объяснение:** Создаём один экземпляр настроек, который можно импортировать в других файлах. При создании автоматически загружаются значения из .env файла.

---

## 2. bot/database/models.py - Модели базы данных

```python
"""
Модели базы данных.

Содержит SQLAlchemy модели для всех таблиц БД.
Используется асинхронный режим SQLAlchemy.
"""
```
**Объяснение:** Здесь описываются все таблицы базы данных в виде Python классов.

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
```
**Объяснение:** Импорты:
- `datetime` - для работы с датами
- `Optional` - для полей, которые могут быть None
- Типы колонок: `BigInteger` (большие числа), `Boolean` (да/нет), `DateTime` (дата/время), `String` (строка), `Text` (длинный текст)
- `ForeignKey` - внешний ключ (связь между таблицами)
- `Index` - индекс для ускорения поиска
- `DeclarativeBase` - базовый класс для моделей
- `Mapped` - аннотация типа для полей
- `mapped_column` - создание колонки
- `relationship` - связь между моделями
- `func` - SQL функции (например, now() для текущего времени)

```python
class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass
```
**Объяснение:** Базовый класс для всех моделей. Все модели будут наследоваться от него. Пока пустой, но можно добавить общие методы.

```python
class User(Base):
    """Модель пользователя бота."""
    
    __tablename__ = "users"
```
**Объяснение:**
- `User` - класс модели пользователя
- `Base` - наследуется от базового класса
- `__tablename__` - имя таблицы в базе данных (users)

```python
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
```
**Объяснение:**
- `id` - поле идентификатора
- `Mapped[int]` - тип данных (целое число)
- `Integer` - тип колонки в БД
- `primary_key=True` - первичный ключ (уникальный идентификатор)
- `autoincrement=True` - автоматическое увеличение (1, 2, 3, ...)

```python
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
```
**Объяснение:**
- `telegram_id` - ID пользователя в Telegram (очень большое число)
- `BigInteger` - тип для больших чисел (Telegram ID может быть очень большим)
- `unique=True` - уникальное значение (не может быть двух пользователей с одинаковым telegram_id)
- `nullable=False` - не может быть пустым (обязательное поле)
- `index=True` - создаётся индекс для быстрого поиска

```python
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```
**Объяснение:**
- `username` - имя пользователя в Telegram (например, @username)
- `Optional[str]` - может быть строкой или None
- `String(255)` - строка максимум 255 символов
- `nullable=True` - может быть пустым (не у всех есть username)

```python
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```
**Объяснение:**
- `is_active` - активен ли пользователь
- `Boolean` - тип да/нет
- `default=True` - по умолчанию True (активен)
- `nullable=False` - обязательно должно быть значение

```python
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
```
**Объяснение:**
- `created_at` - дата создания записи
- `DateTime(timezone=True)` - дата/время с учётом часового пояса
- `server_default=func.now()` - по умолчанию текущее время (устанавливается БД автоматически)
- `nullable=False` - обязательно

```python
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```
**Объяснение:**
- `updated_at` - дата последнего обновления
- `onupdate=func.now()` - автоматически обновляется при изменении записи

```python
    # Связи
    allowed_users: Mapped[list["AllowedUser"]] = relationship(
        "AllowedUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )
```
**Объяснение:**
- `allowed_users` - список разрешений для этого пользователя
- `relationship` - связь с другой моделью
- `"AllowedUser"` - имя модели (в кавычках, потому что определена ниже)
- `back_populates="user"` - обратная связь (в AllowedUser есть поле user)
- `cascade="all, delete-orphan"` - при удалении пользователя удаляются все его разрешения

```python
    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
```
**Объяснение:** Метод для красивого вывода объекта при отладке. Вместо `<User object at 0x...>` будет `<User(telegram_id=123, username=test)>`.

### Класс Group (группа)

```python
class Group(Base):
    """Модель группы Telegram."""
    
    __tablename__ = "groups"
```
**Объяснение:** Модель группы. Аналогично User, но для групп Telegram.

```python
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
```
**Объяснение:** ID группы в Telegram (уникальный, с индексом для быстрого поиска).

### Класс AllowedUser (разрешённый пользователь)

```python
class AllowedUser(Base):
    """Модель разрешенного пользователя в группе."""
    
    __tablename__ = "allowed_users"
```
**Объяснение:** Связующая таблица - показывает, какой пользователь разрешён в какой группе.

```python
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
```
**Объяснение:**
- `user_id` - ID пользователя
- `ForeignKey("users.id")` - внешний ключ на таблицу users, колонку id
- `ondelete="CASCADE"` - при удалении пользователя автоматически удаляется эта запись
- `index=True` - индекс для быстрого поиска

```python
    # Уникальный индекс для пары user_id + group_id
    __table_args__ = (
        Index("idx_allowed_user_group", "user_id", "group_id", unique=True),
    )
```
**Объяснение:** Создаём уникальный индекс на пару (user_id, group_id), чтобы один пользователь не мог быть добавлен в группу дважды.

### Класс GroupMember (участник группы)

```python
class GroupMember(Base):
    """Модель участника группы."""
```
**Объяснение:** Хранит информацию о том, кто сейчас находится в группе (для сравнения с разрешённым списком).

```python
    status: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
```
**Объяснение:** Статус участника: "member", "administrator", "creator" и т.д.

### Класс ActionLog (лог действий)

```python
class ActionLog(Base):
    """Модель лога действий бота."""
```
**Объяснение:** Таблица для логирования всех действий бота (кто что сделал, когда).

```python
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
```
**Объяснение:** Тип действия: "user_removed", "user_allowed", "group_cleanup" и т.д. С индексом для быстрого поиска по типу.

---

## 3. bot/database/connection.py - Подключение к базе данных

```python
"""
Подключение к базе данных.

Содержит функции для создания и управления подключением к БД.
Используется асинхронный режим SQLAlchemy.
"""
```
**Объяснение:** Этот файл отвечает за подключение к базе данных и управление сессиями.

```python
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
```
**Объяснение:**
- `AsyncGenerator` - тип для асинхронных генераторов (используется в get_session)
- `AsyncSession` - асинхронная сессия БД
- `AsyncEngine` - асинхронный движок БД
- `create_async_engine` - функция для создания движка
- `async_sessionmaker` - фабрика для создания сессий
- `NullPool` - пул соединений (для асинхронных операций)

```python
from config import settings
from bot.database.models import Base
```
**Объяснение:** Импортируем настройки и базовый класс моделей.

```python
class Database:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self) -> None:
        """Инициализация подключения к БД."""
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
```
**Объяснение:**
- Класс для управления БД
- `__init__` - конструктор, инициализирует поля как None
- `self.engine` - движок БД (будет создан в initialize)
- `self.session_factory` - фабрика сессий (будет создана в initialize)

```python
    def initialize(self) -> None:
        """Инициализация подключения к базе данных."""
        database_url = (
            f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
```
**Объяснение:**
- `initialize` - метод для инициализации подключения
- `database_url` - строка подключения к PostgreSQL в формате: `postgresql+asyncpg://user:password@host:port/database`
- `asyncpg` - асинхронный драйвер для PostgreSQL

```python
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Установить True для отладки SQL запросов
            poolclass=NullPool,  # Для асинхронных операций
            future=True
        )
```
**Объяснение:**
- `create_async_engine` - создаёт асинхронный движок
- `echo=False` - не выводить SQL запросы в консоль (поставить True для отладки)
- `poolclass=NullPool` - не использовать пул соединений (для async)
- `future=True` - использовать новый API SQLAlchemy

```python
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
```
**Объяснение:**
- `async_sessionmaker` - создаёт фабрику сессий
- `class_=AsyncSession` - тип сессии
- `expire_on_commit=False` - объекты не становятся недействительными после commit
- `autoflush=False` - не делать автоматический flush
- `autocommit=False` - не делать автоматический commit

```python
    async def close(self) -> None:
        """Закрытие подключения к базе данных."""
        if self.engine:
            await self.engine.dispose()
```
**Объяснение:** Закрывает все соединения с БД. Вызывается при завершении работы приложения.

```python
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение сессии БД."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
```
**Объяснение:**
- `get_session` - асинхронный генератор, который возвращает сессию
- `AsyncGenerator[AsyncSession, None]` - тип: генерирует AsyncSession, не возвращает значение
- Проверяем, что БД инициализирована

```python
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
```
**Объяснение:**
- `async with` - асинхронный контекстный менеджер
- `yield session` - отдаём сессию вызывающему коду
- `await session.commit()` - сохраняем изменения (если не было ошибок)
- `except Exception` - если была ошибка, откатываем изменения
- `await session.rollback()` - откат транзакции
- `raise` - пробрасываем ошибку дальше
- `finally` - всегда закрываем сессию

```python
    async def create_tables(self) -> None:
        """Создание всех таблиц в базе данных."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
```
**Объяснение:**
- `create_tables` - создаёт все таблицы в БД на основе моделей
- `self.engine.begin()` - начинаем транзакцию
- `conn.run_sync` - запускаем синхронную функцию в асинхронном контексте
- `Base.metadata.create_all` - создаёт все таблицы из всех моделей

```python
# Глобальный экземпляр БД
db = Database()
```
**Объяснение:** Создаём один экземпляр Database, который можно импортировать везде.

---

## 4. bot/database/repositories/base.py - Базовый репозиторий

```python
"""
Базовый репозиторий.

Содержит базовый класс для всех репозиториев,
реализующий общие методы работы с БД.
"""
```
**Объяснение:** Базовый класс для всех репозиториев. Реализует общие методы (CRUD операции).

```python
from typing import Generic, TypeVar, Type, Optional
from abc import ABC

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)
```
**Объяснение:**
- `Generic` - для создания обобщённых классов
- `TypeVar` - переменная типа (ModelType может быть любой моделью, наследующей Base)
- `ABC` - абстрактный базовый класс
- `select, delete, update` - SQL операции
- `ModelType = TypeVar(...)` - тип модели (User, Group и т.д.)

```python
class BaseRepository(ABC, Generic[ModelType]):
    """Базовый репозиторий для работы с моделями БД."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        """Инициализация репозитория."""
        self.session = session
        self.model = model
```
**Объяснение:**
- `BaseRepository(ABC, Generic[ModelType])` - базовый класс, обобщённый по типу модели
- `__init__` - принимает сессию БД и класс модели
- `self.session` - сохраняем сессию
- `self.model` - сохраняем класс модели (User, Group и т.д.)

```python
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
```
**Объяснение:**
- `get_by_id` - получить запись по ID
- `select(self.model)` - SQL: SELECT * FROM table
- `.where(self.model.id == id)` - WHERE id = ...
- `await self.session.execute` - выполняем запрос
- `result.scalar_one_or_none()` - получаем одну запись или None

```python
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> list[ModelType]:
        """Получить все записи."""
        query = select(self.model).offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
```
**Объяснение:**
- `get_all` - получить все записи с пагинацией
- `.offset(offset)` - пропустить N записей (для пагинации)
- `.limit(limit)` - взять максимум N записей
- `result.scalars().all()` - получить все результаты как список

```python
    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
```
**Объяснение:**
- `create` - создать новую запись
- `self.model(**kwargs)` - создаём экземпляр модели с переданными параметрами
- `self.session.add(instance)` - добавляем в сессию
- `await self.session.flush()` - отправляем в БД (но не коммитим)
- `await self.session.refresh(instance)` - обновляем объект из БД (получаем сгенерированный ID)
- `return instance` - возвращаем созданный объект

```python
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись."""
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(id)
```
**Объяснение:**
- `update` - обновить запись
- `update(self.model)` - SQL: UPDATE table
- `.where(self.model.id == id)` - WHERE id = ...
- `.values(**kwargs)` - SET field1 = value1, field2 = value2
- `await self.session.flush()` - отправляем изменения
- `return await self.get_by_id(id)` - возвращаем обновлённую запись

```python
    async def delete(self, id: int) -> bool:
        """Удалить запись."""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0
```
**Объяснение:**
- `delete` - удалить запись
- `delete(self.model)` - SQL: DELETE FROM table
- `.where(self.model.id == id)` - WHERE id = ...
- `result.rowcount` - количество удалённых строк
- `return result.rowcount > 0` - True, если что-то удалили

---

## 5. bot/database/repositories/user_repository.py - Репозиторий пользователей

```python
"""
Репозиторий для работы с пользователями.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repositories.base import BaseRepository
```
**Объяснение:** Импорты для работы с пользователями.

```python
class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""
    
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория пользователей."""
        super().__init__(session, User)
```
**Объяснение:**
- `UserRepository(BaseRepository[User])` - наследуется от BaseRepository, указываем тип User
- `super().__init__(session, User)` - вызываем конструктор базового класса с моделью User

```python
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
```
**Объяснение:**
- `get_by_telegram_id` - получить пользователя по Telegram ID (не по внутреннему ID БД)
- `select(User).where(User.telegram_id == telegram_id)` - ищем по telegram_id
- Возвращает User или None

```python
    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Получить пользователя или создать нового."""
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
```
**Объяснение:**
- `get_or_create` - получить пользователя или создать, если его нет
- Сначала ищем пользователя по telegram_id
- Если найден - обновляем данные, если они изменились
- Если не найден - создаём нового
- Это удобно при работе с Telegram API, где пользователь может появиться в любой момент

```python
    async def get_active_users(self) -> list[User]:
        """Получить список активных пользователей."""
        result = await self.session.execute(
            select(User).where(User.is_active == True)
        )
        return list(result.scalars().all())
```
**Объяснение:** Получить всех активных пользователей (где is_active = True).

```python
    async def get_admins(self) -> list[User]:
        """Получить список администраторов."""
        result = await self.session.execute(
            select(User).where(User.is_admin == True)
        )
        return list(result.scalars().all())
```
**Объяснение:** Получить всех администраторов бота.

```python
    async def count(self) -> int:
        """Получить количество пользователей."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar() or 0
```
**Объяснение:**
- `count` - подсчитать количество пользователей
- `func.count(User.id)` - SQL: SELECT COUNT(id) FROM users
- `result.scalar()` - получить одно значение (число)
- `or 0` - если None, вернуть 0

---

## 6. bot/database/repositories/group_repository.py - Репозиторий групп

Аналогично UserRepository, но для групп. Основные методы:
- `get_by_telegram_id` - найти группу по Telegram ID
- `get_or_create` - получить или создать группу
- `get_active_groups` - получить активные группы

---

## 7. bot/database/repositories/allowed_user_repository.py - Репозиторий разрешённых пользователей

```python
class AllowedUserRepository(BaseRepository[AllowedUser]):
    """Репозиторий для работы с разрешенными пользователями."""
```
**Объяснение:** Репозиторий для работы с таблицей разрешений (кто может быть в какой группе).

```python
    async def get_by_user_and_group(
        self,
        user_id: int,
        group_id: int
    ) -> Optional[AllowedUser]:
        """Получить разрешение для пользователя в группе."""
        result = await self.session.execute(
            select(AllowedUser).where(
                and_(
                    AllowedUser.user_id == user_id,
                    AllowedUser.group_id == group_id
                )
            )
        )
        return result.scalar_one_or_none()
```
**Объяснение:**
- `get_by_user_and_group` - найти разрешение для конкретного пользователя в конкретной группе
- `and_()` - логическое И (оба условия должны выполняться)
- Ищем запись, где user_id = X И group_id = Y

```python
    async def is_allowed(self, user_id: int, group_id: int) -> bool:
        """Проверить, разрешен ли пользователь в группе."""
        allowed = await self.get_by_user_and_group(user_id, group_id)
        return allowed is not None
```
**Объяснение:** Простая проверка - есть ли разрешение. Возвращает True/False.

```python
    async def get_allowed_telegram_ids_for_group(self, group_id: int) -> list[int]:
        """Получить список Telegram ID разрешенных пользователей для группы."""
        result = await self.session.execute(
            select(User.telegram_id).join(AllowedUser).where(
                AllowedUser.group_id == group_id
            )
        )
        return list(result.scalars().all())
```
**Объяснение:**
- `get_allowed_telegram_ids_for_group` - получить список Telegram ID разрешённых пользователей
- `select(User.telegram_id)` - выбираем только telegram_id
- `.join(AllowedUser)` - присоединяем таблицу разрешений
- `.where(AllowedUser.group_id == group_id)` - фильтруем по группе
- Возвращаем список ID (не объекты User), что быстрее и удобнее для сравнения

---

## 8. bot/database/repositories/group_member_repository.py - Репозиторий участников групп

Аналогично другим репозиториям. Основные методы:
- `add_member` - добавить участника в группу
- `remove_member` - удалить участника
- `get_member_telegram_ids_for_group` - получить список ID участников

---

## 9. bot/database/repositories/action_log_repository.py - Репозиторий логов

```python
    async def create_log(
        self,
        action_type: str,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        details: Optional[str] = None
    ) -> ActionLog:
        """Создать запись в логе."""
        return await self.create(
            action_type=action_type,
            user_id=user_id,
            group_id=group_id,
            target_user_id=target_user_id,
            details=details
        )
```
**Объяснение:** Удобный метод для создания лога. Просто обёртка над `create` с понятными параметрами.

---

## 10. bot/services/group_cleanup_service.py - Сервис очистки групп

```python
"""
Сервис для очистки групп от неразрешенных пользователей.

Реализует основную бизнес-логику бота:
- Получение списка участников группы
- Сравнение с разрешенным списком
- Удаление неразрешенных пользователей
"""
```
**Объяснение:** Это главный сервис - здесь реализована основная логика бота.

```python
from aiogram import Bot
from aiogram.types import ChatMember
```
**Объяснение:** Импорты из aiogram для работы с Telegram API.

```python
class GroupCleanupService:
    """Сервис для очистки групп от неразрешенных пользователей."""
    
    def __init__(self, bot: Bot) -> None:
        """Инициализация сервиса."""
        self.bot = bot
```
**Объяснение:** Сервис принимает экземпляр бота для работы с Telegram API.

```python
    async def cleanup_group(self, group_telegram_id: int) -> dict:
        """Очистить группу от неразрешенных пользователей."""
        result = {
            "removed_count": 0,
            "errors": [],
            "removed_users": []
        }
```
**Объяснение:**
- `cleanup_group` - главный метод очистки группы
- Возвращает словарь с результатами: сколько удалено, ошибки, список удалённых

```python
        try:
            async with db.get_session() as session:
                # Получаем репозитории
                group_repo = GroupRepository(session)
                user_repo = UserRepository(session)
                allowed_repo = AllowedUserRepository(session)
                member_repo = GroupMemberRepository(session)
                log_repo = ActionLogRepository(session)
```
**Объяснение:**
- `async with db.get_session()` - получаем сессию БД (автоматически закроется)
- Создаём все нужные репозитории, передавая им сессию

```python
                # Получаем или создаем группу в БД
                group = await group_repo.get_by_telegram_id(group_telegram_id)
                if not group:
                    chat = await self.bot.get_chat(group_telegram_id)
                    group = await group_repo.get_or_create(
                        telegram_id=group_telegram_id,
                        title=chat.title,
                        username=chat.username
                    )
```
**Объяснение:**
- Ищем группу в БД
- Если не найдена - получаем информацию из Telegram и создаём запись в БД

```python
                # Получаем список участников группы из Telegram
                members = await self._get_group_members(group_telegram_id)
                
                # Получаем список разрешенных пользователей из БД
                allowed_telegram_ids = await allowed_repo.get_allowed_telegram_ids_for_group(
                    group.id
                )
                allowed_set = set(allowed_telegram_ids)
```
**Объяснение:**
- Получаем список участников из Telegram
- Получаем список разрешённых из БД
- Преобразуем в set для быстрого поиска (проверка "есть ли в списке" за O(1))

```python
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
```
**Объяснение:**
- Проходим по всем участникам группы
- Пропускаем ботов
- Создаём или обновляем пользователя в БД
- Добавляем запись о том, что он участник группы

```python
                # Находим пользователей для удаления
                members_to_remove = [
                    member for member in members
                    if not member.user.is_bot
                    and member.user.id not in allowed_set
                    and member.status not in ["creator", "administrator"]
                ]
```
**Объяснение:**
- Список пользователей для удаления:
  - Не бот
  - Нет в списке разрешённых
  - Не создатель и не администратор (их не трогаем)

```python
                # Удаляем неразрешенных пользователей
                for member in members_to_remove:
                    try:
                        await self.bot.ban_chat_member(
                            chat_id=group_telegram_id,
                            user_id=member.user.id
                        )
```
**Объяснение:**
- Для каждого пользователя вызываем API Telegram для бана
- `ban_chat_member` - удаляет пользователя из группы

```python
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
```
**Объяснение:**
- Увеличиваем счётчик удалённых
- Добавляем информацию о пользователе в результат
- Удаляем запись из БД
- Логируем действие

```python
                    except Exception as e:
                        error_msg = f"Failed to remove user {member.user.id}: {str(e)}"
                        result["errors"].append(error_msg)
                        logger.error(error_msg)
```
**Объяснение:** Если не удалось удалить пользователя (например, нет прав), ловим ошибку и добавляем в список ошибок.

```python
    async def add_allowed_user(
        self,
        group_telegram_id: int,
        user_telegram_id: int,
        added_by_telegram_id: int
    ) -> bool:
        """Добавить пользователя в список разрешенных для группы."""
```
**Объяснение:** Метод для добавления пользователя в белый список группы.

```python
    async def remove_allowed_user(
        self,
        group_telegram_id: int,
        user_telegram_id: int
    ) -> bool:
        """Удалить пользователя из списка разрешенных для группы."""
```
**Объяснение:** Метод для удаления пользователя из белого списка.

---

## Итог

Все файлы работают вместе:
1. **config.py** - загружает настройки из .env
2. **models.py** - описывает структуру БД
3. **connection.py** - подключается к БД
4. **repositories/** - работают с данными
5. **services/group_cleanup_service.py** - реализует бизнес-логику

Код следует принципам:
- **SOLID** - каждый класс делает одну вещь
- **DRY** - нет повторений, общий код в базовых классах
- **Асинхронность** - всё работает асинхронно для производительности
- **Типизация** - везде указаны типы для безопасности

