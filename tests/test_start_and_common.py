import pytest

from bot.handlers.common import echo_debug
from bot.handlers.start import cmd_start


class FakeUser:
    def __init__(self, user_id: int = 1, first_name: str = "TestUser"):
        self.id = user_id
        self.first_name = first_name


class FakeMessage:
    def __init__(self, text: str, chat_type: str = "private"):
        self.text = text
        self.from_user = FakeUser()
        self.answers: list[tuple[str, object | None]] = []
        self.chat = type("Chat", (), {"id": 1, "type": chat_type})

    async def answer(self, text: str, reply_markup=None):
        self.answers.append((text, reply_markup))


@pytest.mark.asyncio
async def test_cmd_start_replies_something():
    """
    Стартовая команда должна хотя бы что-то ответить.
    """
    msg = FakeMessage(text="/start")
    await cmd_start(msg)

    assert msg.answers


@pytest.mark.asyncio
async def test_echo_debug_repeats_text():
    """
    echo_debug должен отправить ответ с оригинальным текстом
    """
    msg = FakeMessage(text="hello world")
    await echo_debug(msg)

    assert msg.answers
    text, _ = msg.answers[0]
    assert "hello world" in text


