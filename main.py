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
from bot.handlers import common as common_handlers


CHECK_EVERY_SECONDS = 60 * 60 * 24  # раз в сутки

async def periodic_cleanup(bot: Bot) -> None:
    logging.info("periodic_cleanup: фоновый сервис стартовал")

    while True:
        # собираем чаты: из .env + те, что добавили командами
        dynamic_ids = await user_repo.get_moderated_chats()
        chat_ids = list(set(MODERATED_CHAT_IDS + dynamic_ids))

        if not chat_ids:
            logging.info("periodic_cleanup: чатов нет, просто сплю")
            await asyncio.sleep(CHECK_EVERY_SECONDS)
            continue

        logging.info("periodic_cleanup: проверяю чаты: %s", chat_ids)

        for chat_id in chat_ids:
            try:
                banned_ids = await user_repo.run_check_for_chat(chat_id)
            except Exception as e:
                logging.exception("periodic_cleanup: ошибка при проверке чата %s: %s", chat_id, e)
                continue

            if not banned_ids:
                logging.info("periodic_cleanup: в чате %s нарушителей не нашли", chat_id)
                continue

            for user_id in banned_ids:
                try:
                    await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                    logging.info("periodic_cleanup: забанил %s в чате %s", user_id, chat_id)
                except Exception as e:
                    logging.exception(
                        "periodic_cleanup: не смог забанить %s в чате %s: %s",
                        user_id, chat_id, e,
                    )

        await asyncio.sleep(CHECK_EVERY_SECONDS)


async def setup_commands(bot: Bot) -> None:
    """
    Регистрируем команды, которые будут показываться в меню бота.
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