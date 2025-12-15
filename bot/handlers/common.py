from aiogram import Router, types

router = Router()


@router.message()
async def echo_debug(message: types.Message) -> None:
    await message.answer(f"Я получил: {message.text!r}")