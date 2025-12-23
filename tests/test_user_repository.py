import os

# для тестов используем отдельную SQLite-базу
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_repo.db")

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from bot.database.models import Base
from bot.database.repository import UserRepository

TEST_DB_URL = "sqlite+aiosqlite:///./test_repo.db"

# движок для тестовой бд
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Создаём таблицы один раз для всех тестов репозитория"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture
def repo() -> UserRepository:
    """Отдельный репозиторий, который работает через тестовую SQLite-базу"""
    return UserRepository(session_factory=TestSessionFactory)


@pytest.mark.asyncio
async def test_add_and_remove_from_blacklist(repo: UserRepository):
    # первый раз пользователь добавляется
    ok_first = await repo.add_to_blacklist(user_id=123, username="test_user")
    assert ok_first is True

    # второй раз того же пользователя уже не добавляем
    ok_second = await repo.add_to_blacklist(user_id=123, username="test_user")
    assert ok_second is False

    # удаление существующего пользователя
    removed_first = await repo.remove_from_blacklist(user_id=123)
    assert removed_first is True

    # повторное удаление - уже нечего удалять
    removed_second = await repo.remove_from_blacklist(user_id=123)
    assert removed_second is False


@pytest.mark.asyncio
async def test_run_check_for_chat_returns_list(repo: UserRepository):
    # добавляем пару пользователей в чс
    await repo.add_to_blacklist(user_id=111, username="u1")
    await repo.add_to_blacklist(user_id=222, username="u2")

    result = await repo.run_check_for_chat(chat_id=-100)

    assert isinstance(result, list)
    assert 111 in result
    assert 222 in result