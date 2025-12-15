"""
Простая учебная реализация "базы" для работы с пользователями.

!!! ВАЖНО
Сейчас всё хранится просто в памяти процесса (в глобальных переменных).
После перезапуска бота данные пропадут.

Позже сюда можно будет прикрутить настоящую БД (Postgres + SQLAlchemy),
сохранив те же имена функций, чтобы не переписывать хендлеры.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set


# Чёрный список пользователей: просто id
_blacklist: Set[int] = set()

# Логи действий модерации
_logs: List[Dict[str, object]] = []


async def add_to_blacklist(user_id: int, username: Optional[str] = None) -> bool:
    """
    Добавить пользователя в чёрный список.
    Возвращает True, если добавили, False — если он уже там был.
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
    Удалить пользователя из чёрного списка.
    True — если удалили, False — если его там не было.
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
    Вернуть простую статистику:
    - сколько пользователей в чёрном списке
    - сколько всего действий
    - текст про последнюю операцию (если была)
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
    Учебная версия проверки чата.
    Сейчас просто возвращает список id из чёрного списка,
    будто бы мы их "нашли" в чате и забанили.

    Позже здесь можно будет:
    - спросить у Telegram список участников чата
    - сравнить его с чёрным списком
    - реально вызывать ban/kick.
    """
    # chat_id пока не используем, но аргумент оставляем, чтобы интерфейс не менять
    _ = chat_id
    return list(_blacklist)