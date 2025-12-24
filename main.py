"""
Точка входа в бота.

- создаем Bot и Dispatcher,
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
    Фоновая проверка чатов по расписанию.

    Логика:
    - раз в минуту смотрим время по UTC;
    - если наступило 08:00 UTC и за этот день еще не проверяли,
      то пробегаемся по всем чатам из MODERATED_CHAT_IDS;
    - для каждого чата пытаемся забанить пользователей из черного списка;
    - отправляем краткий отчет в сам чат и админам.
    """
    logger.info("periodic_cleanup: фоновый сервис стартовал")

    last_run_date: dt.date | None = None

    while True:
        now_utc = dt.datetime.utcnow()
        today = now_utc.date()

        # если сейчас 08:00 UTC и мы еще не запускали проверку сегодня
        if now_utc.hour == 8 and last_run_date != today:
            last_run_date = today

            if not MODERATED_CHAT_IDS:
                logger.info("periodic_cleanup: чатов нет, просто отмечаем запуск на сегодня")
            else:
                logger.info(
                    "periodic_cleanup: запускаю ежедневную проверку для чатов: %s",
                    MODERATED_CHAT_IDS,
                )

            for chat_id in MODERATED_CHAT_IDS:
                try:
                    banned_users = await _ban_blacklisted_in_chat(bot, chat_id)
                except Exception:
                    logger.exception("periodic_cleanup: ошибка при проверке чата %s", chat_id)
                    continue

                # текст отчета
                if banned_users:
                    text = (
                        "Ежедневная проверка чата завершена.\n"
                        f"Забанено пользователей по черному списку: {len(banned_users)}\n"
                        + "\n".join(f"- {uid}" for uid in banned_users)
                    )
                else:
                    text = "Ежедневная проверка чата: нарушителей по черному списку не найдено"

                # попытаться отправить отчет в сам чат
                try:
                    await bot.send_message(chat_id, text)
                except Exception:
                    logger.exception("periodic_cleanup: не удалось отправить отчет в чат %s", chat_id)

                # продублировать админам
                for admin_id in ADMIN_IDS:
                    try:
                        await bot.send_message(
                            admin_id,
                            f"[чат {chat_id}] {text}",
                        )
                    except Exception:
                        logger.exception(
                            "periodic_cleanup: не удалось отправить отчет админу %s", admin_id
                        )

        # спим минутку
        await asyncio.sleep(60)


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