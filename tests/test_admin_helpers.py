from types import SimpleNamespace

from bot.handlers.admin import is_admin as is_admin, get_args as get_args
from config import ADMIN_IDS


def test_is_admin_uses_admin_ids():
    """
    Проверяем, что функция смотрит в список ADMIN_IDS
    """

    admin_id = ADMIN_IDS[0] if ADMIN_IDS else 1
    msg_admin = SimpleNamespace(from_user=SimpleNamespace(id=admin_id))
    msg_not_admin = SimpleNamespace(from_user=SimpleNamespace(id=999999))

    assert is_admin(msg_admin) is True
    assert is_admin(msg_not_admin) is False


def test_get_args_parses_command_text():
    assert get_args("/adduser 123") == ["123"]
    assert get_args("/adduser") == []
    assert get_args(None) == []