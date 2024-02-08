from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from lexicon.lexicon import LEXICON_RU
from keyboards.inline_keyboard import get_markup

user_router = Router()


@user_router.message(CommandStart())
async def start_cmd(message: Message):
    markup = get_markup(3, 'start_btn', 'settings_btn', 'info_btn')
    await message.answer(text=LEXICON_RU['/start'], reply_markup=markup)


@user_router.callback_query(F.data == 'info_btn')
async def info_cmd(callback: CallbackQuery):
    markup = get_markup(1, 'backward')
    await callback.message.edit_text(text=LEXICON_RU['info'], reply_markup=markup)


@user_router.callback_query(F.data == 'settings_btn')
async def settings_cmd(callback: CallbackQuery):
    markup = get_markup(1, 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'], reply_markup=markup)


@user_router.callback_query(F.data == 'backward')
async def backward(callback: CallbackQuery):
    markup = get_markup(3, 'start_btn', 'settings_btn', 'info_btn')
    await callback.message.edit_text(text=LEXICON_RU['/start'], reply_markup=markup)


# @user_router.message(F.text.in_(['/help', LEXICON_RU['info_btn']]))
# async def info_cmd(message: Message):
#     await message.answer(text=LEXICON_RU['/help'])


# @user_router.