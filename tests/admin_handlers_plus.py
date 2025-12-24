import pytest

from config import ADMIN_IDS

from bot.handlers import admin as admin_handlers
from bot.database import repository


class FakeFromUser:
    def __init__(self, user_id: int, username: str | None = None):
        self.id = user_id
        self.username = username


class FakeChat:
    def __init__(self, chat_id: int, chat_type: str = "group"):
        self.id = chat_id
        self.type = chat_type


class FakeMessage:
    """
    Простой mock aiogram.types.Message:
    - есть from_user, text, chat, reply_to_message
    - метод answer() запоминает ответы
    """

    def __init__(
        self,
        from_user_id: int,
        text: str | None = None,
        chat_type: str = "group",
        reply_to_message: "FakeMessage | None" = None,
    ):
        self.from_user = FakeFromUser(from_user_id)
        self.text = text
        self.chat = FakeChat(chat_id=-100, chat_type=chat_type)
        self.reply_to_message = reply_to_message
        self.answers: list[str] = []
        self.bot = None

    async def answer(self, text: str) -> None:
        self.answers.append(text)


class FakeBot:
    """
    Упрощенный бот:
    - ban_chat_member() просто запоминает кого "забанили"
    - send_message() запоминает отправленные сообщения
    """

    def __init__(self):
        self.banned: list[tuple[int, int]] = []
        self.messages: list[tuple[int, str]] = []

    async def ban_chat_member(self, chat_id: int, user_id: int) -> None:
        self.banned.append((chat_id, user_id))

    async def send_message(self, chat_id: int, text: str) -> None:
        self.messages.append((chat_id, text))



@pytest.mark.asyncio
async def test_adduser_non_admin(monkeypatch):
    """
    Если команду пишет не админ, репозиторий не трогаем,
    а в ответ прилетает сообщение про права.
    """

    async def fake_add_to_blacklist(*args, **kwargs):
        raise AssertionError("Репозиторий не должен вызываться для неадмина")

    # делаем так, чтобы _is_admin всегда возвращал False
    monkeypatch.setattr(admin_handlers, "_is_admin", lambda msg: False)
    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=123, text="/adduser 111")
    await admin_handlers.add_user_cmd(msg)

    assert msg.answers, "Должно быть хотя бы одно сообщение от бота"
    assert "только для админов" in msg.answers[0]


@pytest.mark.asyncio
async def test_adduser_invalid_argument(monkeypatch):
    """
    Админ, но id некорректный: сообщение об ошибке
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_add_to_blacklist(*args, **kwargs):
        raise AssertionError("Не должны пытаться писать в чс при невалидном id")

    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=admin_id, text="/adduser not_a_number")
    await admin_handlers.add_user_cmd(msg)

    assert msg.answers
    assert "должен быть числом" in msg.answers[0]


@pytest.mark.asyncio
async def test_adduser_no_args_and_no_reply(monkeypatch):
    """
    /adduser без аргументов и без reply_to_message: бот объясняет, как правильно
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_add_to_blacklist(*args, **kwargs):
        raise AssertionError("Не должны вызывать репозиторий без id")

    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=admin_id, text="/adduser")
    await admin_handlers.add_user_cmd(msg)

    assert msg.answers
    text = msg.answers[0]
    assert "Нужно указать id" in text or "Пример: /adduser" in text



@pytest.mark.asyncio
async def test_deluser_no_args(monkeypatch):
    """
    /deluser без аргументов: подсказка, что нужен id
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_remove_from_blacklist(*args, **kwargs):
        raise AssertionError("Репозиторий не должен вызываться без id")

    monkeypatch.setattr(
        repository.user_repo,
        "remove_from_blacklist",
        fake_remove_from_blacklist,
    )

    msg = FakeMessage(from_user_id=admin_id, text="/deluser")
    await admin_handlers.del_user_cmd(msg)

    assert msg.answers
    assert "Нужно указать id" in msg.answers[0]


@pytest.mark.asyncio
async def test_deluser_invalid_argument(monkeypatch):
    """
    /deluser с нечисловым id: сообщение про формат
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_remove_from_blacklist(*args, **kwargs):
        raise AssertionError("Не должны ходить в репозиторий при невалидном id")

    monkeypatch.setattr(
        repository.user_repo,
        "remove_from_blacklist",
        fake_remove_from_blacklist,
    )

    msg = FakeMessage(from_user_id=admin_id, text="/deluser NaN")
    await admin_handlers.del_user_cmd(msg)

    assert msg.answers
    assert "должен быть числом" in msg.answers[0]



@pytest.mark.asyncio
async def test_force_check_non_admin(monkeypatch):
    """
    /force_check от не-админа -> репозиторий и бан-функции не трогаем
    """

    monkeypatch.setattr(admin_handlers, "_is_admin", lambda msg: False)

    async def fake_run_check_for_chat(*args, **kwargs):
        raise AssertionError("Не должны вызывать run_check_for_chat от неадмина")

    monkeypatch.setattr(
        repository.user_repo,
        "run_check_for_chat",
        fake_run_check_for_chat,
    )

    msg = FakeMessage(from_user_id=123, text="/force_check")
    bot = FakeBot()
    msg.bot = bot

    await admin_handlers.cmd_force_check(msg)

    assert msg.answers
    assert "только для админов" in msg.answers[0]


@pytest.mark.asyncio
async def test_force_check_private_chat(monkeypatch):
    """
    /force_check в приватном чате -> подсказка, что команда для групп
    """

    monkeypatch.setattr(admin_handlers, "_is_admin", lambda msg: True)

    async def fake_run_check_for_chat(*args, **kwargs):
        raise AssertionError("Не должны ходить в репозиторий для приватного чата")

    monkeypatch.setattr(
        repository.user_repo,
        "run_check_for_chat",
        fake_run_check_for_chat,
    )

    msg = FakeMessage(from_user_id=1, text="/force_check", chat_type="private")
    bot = FakeBot()
    msg.bot = bot

    await admin_handlers.cmd_force_check(msg)

    assert msg.answers
    assert "группе" in msg.answers[0] or "канале" in msg.answers[0]


@pytest.mark.asyncio
async def test_ban_blacklisted_handles_exceptions(monkeypatch):
    """
    Для _ban_blacklisted_in_chat:
    - один пользователь банится нормально,
    - на втором бан падает исключение, но функция не ломается
    """

    async def fake_run_check_for_chat(chat_id: int):
        # в черном списке два пользователя
        return [111, 222]

    monkeypatch.setattr(
        repository.user_repo,
        "run_check_for_chat",
        fake_run_check_for_chat,
    )

    bot = FakeBot()

    async def broken_ban(chat_id: int, user_id: int):
        if user_id == 222:
            raise RuntimeError("упали на втором пользователе")
        bot.banned.append((chat_id, user_id))

    monkeypatch.setattr(bot, "ban_chat_member", broken_ban)

    banned = await admin_handlers._ban_blacklisted_in_chat(bot, chat_id=-100)

    # забанили только первого, но функция не упала
    assert banned == [111]


@pytest.mark.asyncio
async def test_adduser_success(monkeypatch):
    """
    /adduser с валидным числовым id от админа
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    called = {}

    async def fake_add_to_blacklist(user_id: int, username: str | None = None) -> bool:
        called["args"] = (user_id, username)
        return True

    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=admin_id, text="/adduser 12345")
    await admin_handlers.add_user_cmd(msg)

    assert "args" in called
    assert called["args"][0] == 12345
    assert msg.answers


@pytest.mark.asyncio
async def test_adduser_already_in_blacklist(monkeypatch):
    """
    /adduser, но репозиторий говорит, что пользователь уже есть в чс
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_add_to_blacklist(user_id: int, username: str | None = None) -> bool:
        return False  # уже в чс

    monkeypatch.setattr(repository.user_repo, "add_to_blacklist", fake_add_to_blacklist)

    msg = FakeMessage(from_user_id=admin_id, text="/adduser 999")
    await admin_handlers.add_user_cmd(msg)

    assert msg.answers


@pytest.mark.asyncio
async def test_deluser_success(monkeypatch):
    """
    /deluser с валидным id: пользователь найден и удален
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    called = {}

    async def fake_remove_from_blacklist(user_id: int) -> bool:
        called["user_id"] = user_id
        return True

    monkeypatch.setattr(
        repository.user_repo,
        "remove_from_blacklist",
        fake_remove_from_blacklist,
    )

    msg = FakeMessage(from_user_id=admin_id, text="/deluser 777")
    await admin_handlers.del_user_cmd(msg)

    assert called.get("user_id") == 777
    assert msg.answers


@pytest.mark.asyncio
async def test_deluser_not_found(monkeypatch):
    """
    /deluser, но такого пользователя нет в чс
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_remove_from_blacklist(user_id: int) -> bool:
        return False

    monkeypatch.setattr(
        repository.user_repo,
        "remove_from_blacklist",
        fake_remove_from_blacklist,
    )

    msg = FakeMessage(from_user_id=admin_id, text="/deluser 555")
    await admin_handlers.del_user_cmd(msg)

    assert msg.answers


@pytest.mark.asyncio
async def test_stats_success(monkeypatch):
    """
    /stats от админа: репозиторий вызывается, бот что-то отвечает.
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_get_stats():
        return {
            "blacklist_count": 3,
            "total_actions": 5,
            "last_action": "ban 123",
        }

    monkeypatch.setattr(repository.user_repo, "get_stats", fake_get_stats)

    msg = FakeMessage(from_user_id=admin_id, text="/stats")
    await admin_handlers.stats_cmd(msg)

    assert msg.answers


@pytest.mark.asyncio
async def test_force_check_bans_users_in_group(monkeypatch):
    """
    /force_check в группе от админа
    """
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1

    async def fake_run_check_for_chat(chat_id: int):
        # нашли трех нарушителей
        return [101, 202, 303]

    monkeypatch.setattr(
        repository.user_repo,
        "run_check_for_chat",
        fake_run_check_for_chat,
    )

    bot = FakeBot()
    msg = FakeMessage(from_user_id=admin_id, text="/force_check", chat_type="group")
    msg.bot = bot

    await admin_handlers.cmd_force_check(msg)

    assert bot.banned
    assert msg.answers


