import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.handlers import start as start_handlers
from bot.handlers import admin as admin_handlers
from bot.handlers import common as common_handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN пустой. Проверь файл .env")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML),)
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем роутеры с хендлерами
    dp.include_router(start_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(common_handlers.router)

    #убираем webhook и старые апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    print("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
