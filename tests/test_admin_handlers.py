from types import SimpleNamespace

import pytest

from bot.handlers.admin import add_user_cmd, del_user_cmd, stats_cmd, cmd_force_check
from bot.database import repository
from config import ADMIN_IDS


class FakeMessage:
    def __init__(self, from_user_id: int, chat_id: int, text: str):
        self.from_user = SimpleNamespace(id=from_user_id)
        self.chat = SimpleNamespace(id=chat_id)
        self.text = text
        self.reply_to_message = None
        self._answers: list[str] = []
        self.bot = SimpleNamespace()

    async def answer(self, text: str, reply_markup=None):
        self._answers.append(text)


class FakeBot:
    def __init__(self):
        self.ban_calls: list[tuple[int, int]] = []

    async def ban_chat_member(self, chat_id: int, user_id: int) -> None:
        self.ban_calls.append((chat_id, user_id))


@pytest.mark.asyncio
async def test_add_user_cmd_calls_repo_for_admin(monkeypatch):
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    called: dict[str, int] = {}

    async def fake_add_to_blacklist(user_id: int, username=None) -> bool:
        called["user_id"] = user_id
        return True

    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=admin_id, chat_id=-100, text="/adduser 123")
    await add_user_cmd(msg)

    assert msg._answers, "хендлер /adduser ничего не ответил"
    assert called.get("user_id") == 123


@pytest.mark.asyncio
async def test_del_user_cmd_calls_repo_for_admin(monkeypatch):
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    called: dict[str, int] = {}

    async def fake_remove_from_blacklist(user_id: int) -> bool:
        called["user_id"] = user_id
        return True

    monkeypatch.setattr(repository.user_repo, "remove_from_blacklist", fake_remove_from_blacklist)

    msg = FakeMessage(from_user_id=admin_id, chat_id=-100, text="/deluser 123")
    await del_user_cmd(msg)

    assert msg._answers, "хендлер /deluser ничего не ответил"
    assert called.get("user_id") == 123


@pytest.mark.asyncio
async def test_stats_cmd_uses_repo(monkeypatch):
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_get_stats():
        return {
            "blacklist_count": 5,
            "total_actions": 10,
            "last_action": "test_action",
        }

    monkeypatch.setattr(repository.user_repo, "get_stats", fake_get_stats)

    msg = FakeMessage(from_user_id=admin_id, chat_id=-100, text="/stats")
    await stats_cmd(msg)

    assert msg._answers
    joined = "\n".join(msg._answers)
    # проверяем, что в тексте есть наши числа
    assert "5" in joined or "10" in joined


@pytest.mark.asyncio
async def test_cmd_force_check_bans_users(monkeypatch):
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_run_check_for_chat(chat_id: int):
        return [111, 222]

    monkeypatch.setattr(repository.user_repo, "run_check_for_chat", fake_run_check_for_chat)

    bot = FakeBot()
    msg = FakeMessage(from_user_id=admin_id, chat_id=-100, text="/force_check")
    msg.bot = bot

    await cmd_force_check(msg)

    assert bot.ban_calls, "force_check не попытался никого забанить"
    assert msg._answers, "force_check ничего не ответил в чат"