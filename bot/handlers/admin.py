from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.markdown import hcode

from config import ADMIN_IDS
from bot.database.repository import user_repo

router = Router()


def is_admin(msg: types.Message) -> bool:
    if msg.from_user is None:
        return False
    return msg.from_user.id in ADMIN_IDS


def get_args(text: str | None) -> list[str]:
    if not text:
        return []
    parts = text.split()
    if len(parts) <= 1:
        return []
    return parts[1:]


@router.message(Command("adduser"))
async def add_user_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Команда только для админов.")
        return

    args = get_args(message.text)
    user_id = None
    username = None

    # вариант: /adduser 123456789
    if args:
        raw = args[0]
        try:
            user_id = int(raw)
        except ValueError:
            await message.answer("id должен быть числом, а не " + hcode(raw))
            return

    # вариант: /adduser как реплай
    if user_id is None and message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username

    if user_id is None:
        await message.answer(
            "Нужно указать id или ответить командой на сообщение юзера.\n"
            "Пример: /adduser 123456789"
        )
        return

    ok = await user_repo.add_to_blacklist(user_id=user_id, username=username)
    if ok:
        await message.answer(f"Ок, {user_id} добавлен в чёрный список.")
    else:
        await message.answer(f"{user_id} уже был в чёрном списке.")


@router.message(Command("deluser"))
async def del_user_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Команда только для админов.")
        return

    args = get_args(message.text)
    if not args:
        await message.answer("Нужно указать id. Пример: /deluser 123456789")
        return

    raw = args[0]
    try:
        user_id = int(raw)
    except ValueError:
        await message.answer("id должен быть числом.")
        return

    deleted = await user_repo.remove_from_blacklist(user_id=user_id)
    if deleted:
        await message.answer(f"{user_id} убран из чёрного списка.")
    else:
        await message.answer(f"{user_id} в чёрном списке не найден.")


@router.message(Command("stats"))
async def stats_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Статистика только для админов.")
        return

    stats = await user_repo.get_stats()

    text = [
        "📊 Стата по модерации:",
        f"- в чёрном списке: {stats['blacklist_count']}",
        f"- всего действий: {stats['total_actions']}",
    ]
    if stats.get("last_action"):
        text.append(f"- последнее действие: {stats['last_action']}")

    await message.answer("\n".join(text))


@router.message(Command("force_check"))
async def cmd_force_check(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Эта команда только для админов, сорян(")
        return

    await message.answer("Окей, пройдемся по черному списку и забаним, кого надо")

    #берем id из нашего репозитория
    banned_users = await user_repo.run_check_for_chat(message.chat.id)

    if not banned_users:
        await message.answer("В чёрном списке никого нет, банить некого)")
        return

    actually_banned: list[int] = []
    failed: list[int] = []

    for uid in banned_users:
        try:
            # тут запрос в тг
            await message.bot.ban_chat_member(chat_id=message.chat.id, user_id=uid)
            actually_banned.append(uid)
        except Exception:
            failed.append(uid)

    lines: list[str] = []
    if actually_banned:
        lines.append(f"Забанили пользователей: {len(actually_banned)}")
        for uid in actually_banned:
            lines.append(f"- {uid}")

    if failed:
        lines.append("")
        lines.append("Не получилось забанить (нет прав или пользователя уже нет в чате):")
        for uid in failed:
            lines.append(f"- {uid}")

    await message.answer("\n".join(lines))


@router.message(Command("addchat"))
async def add_chat_cmd(message: types.Message) -> None:
    """Добавляем текущий чат в список тех, которые бот будет чистить по расписанию"""
    if not _is_admin(message):
        await message.answer("Эта команда только для админов.")
        return

    chat_id = message.chat.id
    added = await user_repo.add_moderated_chat(chat_id)

    if added:
        await message.answer(f"Ок, запомнил этот чат ({chat_id}) как чат для периодической проверки.")
    else:
        await message.answer("Этот чат уже был в списке, ничего не поменял.")


@router.message(Command("delchat"))
async def del_chat_cmd(message: types.Message) -> None:
    """Убираем текущий чат из списка для периодической проверки"""
    if not _is_admin(message):
        await message.answer("Эта команда только для админов.")
        return

    chat_id = message.chat.id
    removed = await user_repo.remove_moderated_chat(chat_id)

    if removed:
        await message.answer(f"Убрал этот чат ({chat_id}) из списка для периодической проверки.")
    else:
        await message.answer("Этого чата и так не было в списке.")