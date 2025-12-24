from aiogram import Dispatcher

from . import start, admin, common


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(common.router)


__all__ = ["register_all_handlers"]