import asyncio
import logging

from aiogram.filters import Command

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.start import router as start_router
from bot.handlers.common import router as common_router
from bot.handlers.admin import router as admin_router
from bot.handlers import admin as admin_handlers, register_all_handlers

from config import BOT_TOKEN

# Базовая настройка логов
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dasha_bot")


async def main() -> None:
    """Точка входа для запуска бота."""
    # Создаем бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Память — обычное in-memory хранилище FSM
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем все хендлеры
    register_all_handlers(dp)

    # Явно регистрируем команды админа
    dp.message.register(admin_handlers.stats_cmd, Command("stats"))
    dp.message.register(admin_handlers.cmd_force_check, Command("force_check"))
    dp.message.register(admin_handlers.add_user_cmd, Command("adduser"))
    dp.message.register(admin_handlers.del_user_cmd, Command("deluser"))

    logger.info("Bot is starting...")

    try:
        # Запускаем long-polling
        await dp.start_polling(bot)
    finally:
        logger.info("Bot is shutting down...")


if __name__ == "__main__":
    asyncio.run(main())