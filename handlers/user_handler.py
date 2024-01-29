from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from lexicon.lexicon import LEXICON_RU

user_router = Router()


@user_router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(text=LEXICON_RU['/start'])


@user_router.message(F.text.in_(['/help', LEXICON_RU['info_btn']]))
async def info_cmd(message: Message):
    await message.answer(text=LEXICON_RU['/help'])