from aiogram import Router
from aiogram.types import Message
from keyboards.inline_keyboard import get_markup
from lexicon.lexicon import LEXICON_RU


other_router = Router()


@other_router.message()
async def other_msg(message: Message):
    markup = get_markup(1, backward='❌')
    await message.delete()
    await message.answer(text=LEXICON_RU['other'], reply_markup=markup)