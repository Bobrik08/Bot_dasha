from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.markdown import hcode

from config import ADMIN_IDS
from bot.database import user as user_db

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

    ok = await user_db.add_to_blacklist(user_id=user_id, username=username)
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

    deleted = await user_db.remove_from_blacklist(user_id=user_id)
    if deleted:
        await message.answer(f"{user_id} убран из чёрного списка.")
    else:
        await message.answer(f"{user_id} в чёрном списке не найден.")


@router.message(Command("stats"))
async def stats_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Статистика только для админов.")
        return

    stats = await user_db.get_stats()

    text = [
        "📊 Стата по модерации:",
        f"- в чёрном списке: {stats['blacklist_count']}",
        f"- всего действий: {stats['total_actions']}",
    ]
    if stats.get("last_action"):
        text.append(f"- последнее действие: {stats['last_action']}")

    await message.answer("\n".join(text))


@router.message(Command("force_check"))
async def force_check_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("Эту штуку могут запускать только админы.")
        return

    await message.answer("Пробую проверить участников (учебная проверка)...")

    banned_users = await user_db.run_check_for_chat(message.chat.id)

    if not banned_users:
        await message.answer("Нарушителей не нашли, всё ок ✅")
        return

    lines = [f"Нашли в чёрном списке: {len(banned_users)}"]
    for uid in banned_users:
        lines.append(f"- {uid}")
    await message.answer("\n".join(lines))