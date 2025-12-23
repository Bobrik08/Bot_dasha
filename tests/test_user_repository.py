import pytest

from bot.database.repository import user_repo


@pytest.mark.asyncio
async def test_add_and_remove_from_blacklist():
    """
    тест на:
    - добавили пользователч в чс,
    - убедились, что он там есть,
    - удалили, посмотрели, что счётчик не вырос.
    """

    # добавляем пользователя
    ok_added = await user_repo.add_to_blacklist(user_id=123, username="testuser")
    assert ok_added is True

    stats_after_add = await user_repo.get_stats()
    assert stats_after_add["blacklist_count"] >= 1

    # повторное добавление того же id - должно вернуть False
    ok_second = await user_repo.add_to_blacklist(user_id=123, username="testuser")
    assert ok_second is False

    # удаляем пользователя из чс
    ok_deleted = await user_repo.remove_from_blacklist(user_id=123)
    assert ok_deleted is True

    stats_after_delete = await user_repo.get_stats()
    # проверка счетчика
    assert stats_after_delete["blacklist_count"] <= stats_after_add["blacklist_count"]


@pytest.mark.asyncio
async def test_run_check_for_chat_returns_list():
    """
    проверяем, что проверка возвращает список id
    """
    await user_repo.add_to_blacklist(user_id=111, username=None)
    await user_repo.add_to_blacklist(user_id=222, username=None)

    banned = await user_repo.run_check_for_chat(chat_id=1)

    assert isinstance(banned, list)
    assert 111 in banned or 222 in banned