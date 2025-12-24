from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/stats"), KeyboardButton(text="/force_check")],
        ],
        resize_keyboard=True,
    )

    text_lines = [
        "Привет!",
        "Я бот-модератор чата.",
        "",
        "Мои команды:",
        "/stats — статистика",
        "/force_check — проверить участников",
        "/adduser ID — добавить пользователя по его ID в чёрный список",
        "/deluser ID — убрать пользователя из чёрного списка",
    ]

    await message.answer("\n".join(text_lines), reply_markup=kb)