from aiogram import Router, types

router = Router()


@router.message()
async def fallback(message: types.Message) -> None:
    if not message.text:
        return

    await message.answer(
        "Я пока понимаю только команды из меню и простые текстовые штуки\n"
        "Попробуй /start или нажми на команды бота."
    )