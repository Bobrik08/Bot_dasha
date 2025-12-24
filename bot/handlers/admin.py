from __future__ import annotations

from typing import List, Optional, Tuple

from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

import config
from bot.database.repository import user_repo

router = Router()

def _is_admin(message: Any) -> bool:
    user = getattr(message, "from_user", None)
    user_id = getattr(user, "id", None)
    if user_id is None:
        return False

    admin_ids = getattr(config, "ADMIN_IDS", []) or []

    # если список админов пустой – по умолчанию считаем, что admin_id = 1
    if not admin_ids:
        return user_id == 1

    return user_id in admin_ids


def _get_args(message: Any) -> List[str]:
    if isinstance(message, str):
        text = message.strip()
    else:
        text = (getattr(message, "text", "") or "").strip()

    if not text.startswith("/"):
        return []

    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return []

    return parts[1].split()




def _extract_target_user(
    message: types.Message,
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Пытаемся вытащить id пользователя и username из сообщения
    """
    # Вариант 1: команда в ответ на сообщение пользователя
    reply = getattr(message, "reply_to_message", None)
    if reply is not None and getattr(reply, "from_user", None) is not None:
        reply_user = reply.from_user
        uid = getattr(reply_user, "id", None)
        uname = getattr(reply_user, "username", None)
        if uid is not None:
            return uid, uname, None

    # Вариант 2: id передан в аргументах
    args = _get_args(message)
    if not args:
        # Тесты ищут подстроку "Нужно указать id"
        return None, None, "Нужно указать id"

    raw_id = args[0]
    try:
        uid = int(raw_id)
    except (TypeError, ValueError):
        # Тесты ищут подстроку "должен быть числом"
        return None, None, "id должен быть числом"

    # username из текста не выдергиваем, оставляем None
    return uid, None, None


@router.message(Command("adduser"))
async def add_user_cmd(message: types.Message) -> None:
    """
    /adduser <id> - добавить пользователя в черный список.

    Можно:
        /adduser 123
    или ответом на сообщение пользователя:
        (reply) /adduser
    """
    if not _is_admin(message):
        await message.answer("Команда только для админов.")
        return

    user_id, username, error = _extract_target_user(message)
    if error:
        await message.answer(error)
        return

    # user_id здесь гарантированно не None
    added = await user_repo.add_to_blacklist(user_id=user_id, username=username)

    if added:
        await message.answer(f"Пользователь {user_id} добавлен в черный список.")
    else:
        await message.answer("Этот пользователь уже в черном списке.")


@router.message(Command("deluser"))
async def del_user_cmd(message: types.Message) -> None:
    """
    /deluser <id> - удалить пользователя из черного списка
    """
    if not _is_admin(message):
        await message.answer("Команда только для админов.")
        return

    user_id, _username, error = _extract_target_user(message)
    if error:
        await message.answer(error)
        return

    deleted = await user_repo.remove_from_blacklist(user_id=user_id)

    if deleted:
        await message.answer(f"Пользователь {user_id} удален из черного списка.")
    else:
        await message.answer("Этого пользователя нет в черном списке.")


@router.message(Command("stats"))
async def stats_cmd(message: types.Message) -> None:
    """
    /stats - показать статистику по черному списку
    """
    if not _is_admin(message):
        await message.answer("Команда только для админов.")
        return

    stats = await user_repo.get_stats()
    blacklist_count = stats.get("blacklist_count", 0)
    total_actions = stats.get("total_actions", 0)
    last_action = stats.get("last_action") or "нет данных"

    text = (
        "Статистика только для админов:\n"
        f"- В черном списке: {blacklist_count}\n"
        f"- Всего действий: {total_actions}\n"
        f"- Последнее действие: {last_action}"
    )
    await message.answer(text)


async def _ban_blacklisted_in_chat(bot: Bot, chat_id: int) -> list[int]:
    """
    Вспомогательная функция
    """
    bad_ids = await user_repo.run_check_for_chat(chat_id)
    banned: list[int] = []

    for user_id in bad_ids:
        try:
            # В тестах у FakeBot есть именно ban_chat_member
            await bot.ban_chat_member(chat_id, user_id)
        except TelegramBadRequest:
            # Если не получилось забанить (нет прав, нет в чате и т.п.) - просто пропускаем
            continue
        else:
            banned.append(user_id)

    return banned


@router.message(Command("force_check"))
async def cmd_force_check(message: types.Message) -> None:
    """
    /force_check - вручную запустить проверку текущего чата
    """
    if not _is_admin(message):
        await message.answer("Команда только для админов.")
        return

    # защита от приватных чатов
    chat = getattr(message, "chat", None)
    chat_type = getattr(chat, "type", None)
    if chat_type == "private":
        await message.answer("Эта команда работает только в группах и каналах.")
        return

    chat_id = getattr(chat, "id", None)
    if chat_id is None:
        await message.answer("Не получилось определить id чата :(")
        return

    bot: Bot = message.bot  # type: ignore[assignment]

    banned_users = await _ban_blacklisted_in_chat(bot, chat_id)

    if not banned_users:
        await message.answer("Проверила чат, никого не пришлось банить.")
        return

    banned_str = ", ".join(str(uid) for uid in banned_users)
    await message.answer(
        f"Проверила чат.\n"
        f"Забанила пользователей с id: {banned_str}\n"
        f"Всего забанено: {len(banned_users)}"
    )


is_admin = _is_admin
get_args = _get_args