import pytest

from bot.database import user as user_db


@pytest.mark.asyncio
async def test_add_to_blacklist_basic():
    """
    Проверяем простую логику
    """
    ok_first = await user_db.add_to_blacklist(user_id=123, username="testuser")
    ok_second = await user_db.add_to_blacklist(user_id=123, username="testuser")

    assert ok_first is True
    assert ok_second is False


@pytest.mark.asyncio
async def test_remove_from_blacklist_basic():
    """
    Сначала добавляем id, потом удаляем
    """
    await user_db.add_to_blacklist(user_id=456, username=None)

    deleted_first = await user_db.remove_from_blacklist(user_id=456)
    deleted_second = await user_db.remove_from_blacklist(user_id=456)

    assert deleted_first is True
    assert deleted_second is False


@pytest.mark.asyncio
async def test_get_stats_structure():
    """
    get_stats должен возвращать словарь с нужными ключами
    """
    stats = await user_db.get_stats()

    assert isinstance(stats, dict)
    assert "blacklist_count" in stats
    assert "total_actions" in stats


@pytest.mark.asyncio
async def test_run_check_for_chat_returns_list():
    """
    run_check_for_chat просто возвращает список id из чс
    """
    await user_db.add_to_blacklist(user_id=777, username=None)
    await user_db.add_to_blacklist(user_id=888, username=None)

    result = await user_db.run_check_for_chat(chat_id=-100)

    assert isinstance(result, list)
    assert all(isinstance(x, int) for x in result)