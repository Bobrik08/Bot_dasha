"""
Точка входа в бота.

- создаём Bot и Dispatcher,
- подтягиваем хендлеры,
- по желанию включаем фоновую чистку чатов,
- запускаем polling.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand


from config import BOT_TOKEN, MODERATED_CHAT_IDS
from bot.database.repository import user_repo
from bot.database.connection import init_db
from bot.handlers import start as start_handlers
from bot.handlers import admin as admin_handlers
from bot.database.repository import user_repo
from bot.handlers import common as common_handlers


CHECK_EVERY_SECONDS = 60 * 60 * 24  # раз в сутки

async def periodic_cleanup(bot: Bot) -> None:
    """
    Фоновая чистка чатов по чс
    """
    logging.info("periodic_cleanup: фоновый сервис стартовал")

    while True:
        chats_from_config = list(MODERATED_CHAT_IDS)

        # чаты, добавленные через /addchat и хранящиеся в бд
        try:
            chats_from_db = await user_repo.get_moderated_chats()
        except Exception as exc:
            logging.error("periodic_cleanup: не смогли получить чаты из БД: %r", exc)
            chats_from_db = []

        # объединяем, убираем дубли
        chats = sorted({*chats_from_config, *chats_from_db})

        if not chats:
            logging.info("periodic_cleanup: чатов нет, просто сплю")
            await asyncio.sleep(CLEANUP_EVERY_SECONDS)
            continue

        for chat_id in chats:
            banned = await admin_handlers._ban_blacklisted_in_chat(bot, chat_id)
            logging.info(
                "periodic_cleanup: чат %s, забанили %d пользователей из чёрного списка",
                chat_id,
                len(banned),
            )

        await asyncio.sleep(CLEANUP_EVERY_SECONDS)


async def setup_commands(bot: Bot) -> None:
    """
    Регистрируем команды, которые будут показываться в меню бота
    """
    commands = [
        BotCommand(command="start",       description="краткая справка и проверка, что бот жив"),
        BotCommand(command="adduser",     description="добавить пользователя в чс"),
        BotCommand(command="deluser",     description="достать пользователя из чс"),
        BotCommand(command="stats",       description="посмотреть статистику по банам"),
        BotCommand(command="force_check", description="ручная проверка и бан нарушителей в чате"),
        BotCommand(command="addchat",     description="добавить этот чат в список проверяемых"),
        BotCommand(command="delchat",     description="убрать этот чат из списка проверяемых"),
    ]

    await bot.set_my_commands(commands)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await init_db()

    # создаем обычного aiogram-бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    await setup_commands(bot)

    dp = Dispatcher()

    # подключаем роутеры
    dp.include_router(start_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(common_handlers.router)

    asyncio.create_task(periodic_cleanup(bot))

    print("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())