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
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню настроек")


@user_router.callback_query(F.data == 'capacity_btn')
async def capacity_choice(callback: CallbackQuery):
    markup = get_markup(2, cap_1='1', cap_2='10', cap_3='100', cap_4='1000', cap_5='10000')
    await callback.message.edit_text(text=LEXICON_RU['capacity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает разрядность чисел')


@user_router.callback_query(F.data.in_(['cap_1', 'cap_2', 'cap_3', 'cap_4', 'cap_5']))
async def capacity_done(callback: CallbackQuery):
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} выбрал разрядность и находится в меню настроек")


@user_router.callback_query(F.data == 'quantity_btn')
async def quantity_choice(callback: CallbackQuery):
    q = map(str, range(2, 19))
    print(q)
    markup = get_markup(3, *q)
    await callback.message.edit_text(text=LEXICON_RU['quantity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает кол-во действий')


@user_router.callback_query(F.data.in_(map(str, range(2, 19))))
async def quantity_done(callback: CallbackQuery):
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} выбрал кол-во действий и находится в меню настроек")


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