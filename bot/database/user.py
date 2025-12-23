from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set

# чаты, которые мы хотим проверять по расписанию
_moderated_chats: set[int] = set()

# Черный список пользователей: просто id
_blacklist: Set[int] = set()

# Логи действий модерации
_logs: List[Dict[str, object]] = []


async def add_to_blacklist(user_id: int, username: Optional[str] = None) -> bool:
    """
    Добавить пользователя в черный список.
    Возвращает True, если добавили, False - если он уже там был.
    """
    global _blacklist, _logs

    if user_id in _blacklist:
        return False

    _blacklist.add(user_id)
    _logs.append(
        {
            "user_id": user_id,
            "action": "add",
            "username": username,
            "timestamp": datetime.now(),
        }
    )
    return True


async def remove_from_blacklist(user_id: int) -> bool:
    """
    Удалить пользователя из черного списка.
    True - если удалили, False - если его там не было.
    """
    global _blacklist, _logs

    if user_id not in _blacklist:
        return False

    _blacklist.remove(user_id)
    _logs.append(
        {
            "user_id": user_id,
            "action": "remove",
            "timestamp": datetime.now(),
        }
    )
    return True


async def get_stats() -> Dict[str, object]:
    """
    Вернуть простую статистику
    """
    blacklist_count = len(_blacklist)
    total_actions = len(_logs)

    last_action_text: Optional[str] = None
    if _logs:
        last = _logs[-1]
        when = last.get("timestamp")
        action = last.get("action")
        user_id = last.get("user_id")
        last_action_text = f"{action} user_id={user_id} в {when}"

    return {
        "blacklist_count": blacklist_count,
        "total_actions": total_actions,
        "last_action": last_action_text,
    }


async def run_check_for_chat(chat_id: int) -> List[int]:
    """
    Возвращает список пользователей, которых имеет смысл проверить/забанить в чате
    """
    _logs.append(
        {
            "action": "check_chat",
            "chat_id": chat_id,
            "count": len(_blacklist),
            "timestamp": datetime.utcnow(),
        }
    )

    # возвращаем список id из черного списка
    return list(_blacklist)


async def add_moderated_chat(chat_id: int) -> bool:
    """
    Добавляем чат в список тех, которые надо проверять
    True - если реально новый, False - уже был
    """
    if chat_id in _moderated_chats:
        return False
    _moderated_chats.add(chat_id)
    return True


async def remove_moderated_chat(chat_id: int) -> bool:
    """
    Убираем чат из списка для проверки
    """
    if chat_id not in _moderated_chats:
        return False
    _moderated_chats.remove(chat_id)
    return True


async def get_moderated_chats() -> list[int]:
    """
    Просто отдаем текущий список чатов из памяти
    """
    return list(_moderated_chats)