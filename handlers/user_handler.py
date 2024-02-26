import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from lexicon.lexicon import LEXICON_RU
from keyboards.inline_keyboard import get_markup
from aiogram.exceptions import TelegramBadRequest
from time import sleep
from services.services import generate_numbers

user_router = Router()

logger = logging.getLogger(__name__)

@user_router.message(CommandStart())
async def start_cmd(message: Message):
    markup = get_markup(2, 'start_btn', 'settings_btn', 'info_btn')
    await message.answer(text=LEXICON_RU['/start'], reply_markup=markup)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@user_router.callback_query(F.data == 'info_btn')
async def info_cmd(callback: CallbackQuery):
    markup = get_markup(1, 'backward')
    await callback.message.edit_text(text=LEXICON_RU['info'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню информации")


@user_router.callback_query(F.data == 'settings_btn')
async def settings_cmd(callback: CallbackQuery):
    markup = get_markup(1, 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню настроек")


@user_router.callback_query(F.data == "start_btn")
async def start_math(callback: CallbackQuery):
    logger.info(f"Пользователь {callback.from_user.id} запустил логику")
    markup = get_markup(1, 'backward')
    digits = generate_numbers(10)
    for i in range(5, 0, -1):
        await callback.message.edit_text(
            text=f"<b>Начало через {i}...</b>"
        )
        sleep(0.5)

    for number in digits:
        try:
            await callback.message.edit_text(
                text=f"<b>{number}</b>"
            )
            sleep(1)
        except TelegramBadRequest:
            continue

    await callback.message.edit_text(
        text=f"<b>Ответ: {sum(digits)}</b>",
        reply_markup=markup
    )


@user_router.callback_query(F.data == 'backward')
async def backward(callback: CallbackQuery):
    markup = get_markup(2, 'start_btn', 'settings_btn', 'info_btn')
    await callback.message.edit_text(text=LEXICON_RU['/start'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} вернулся в меню")


# @user_router.message(F.text.in_(['/help', LEXICON_RU['info_btn']]))
# async def info_cmd(message: Message):
#     await message.answer(text=LEXICON_RU['/help'])


# @user_router.