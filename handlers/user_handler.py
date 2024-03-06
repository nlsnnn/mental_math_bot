import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from lexicon.lexicon import LEXICON_RU
from keyboards.inline_keyboard import get_markup
from aiogram.exceptions import TelegramBadRequest
from time import sleep
from services.services import generate_numbers, edit_call, generate_dict_quan
from db.requests import (orm_add_user, orm_get_capacity, orm_get_quantity,
                         orm_get_values, orm_update_capacity, orm_update_quantity)

user_router = Router()

logger = logging.getLogger(__name__)

@user_router.message(CommandStart())
async def start_cmd(message: Message, session: AsyncSession):
    user = message.from_user
    await orm_add_user(
        session,
        tg_id=user.id,
        name=user.first_name,
        capacity=1,
        quantity=2
    )

    markup = get_markup(2, 'start_btn', 'settings_btn', 'info_btn')
    await message.answer(text=LEXICON_RU['/start'], reply_markup=markup)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@user_router.message(Command('get_capac'))
async def get_c(message: Message, session: AsyncSession):
    capac = await orm_get_capacity(session, message.from_user.id)

    await message.answer(f"Разрядность: {capac}")


@user_router.message(Command('get_quan'))
async def get_q(message: Message, session: AsyncSession):
    quan = await orm_get_quantity(session, message.from_user.id)

    await message.answer(f"Кол-во действий: {quan}")


@user_router.message(Command('change_capac'))
async def update_c(message: Message, session: AsyncSession):
    new_c = int(message.text.split()[-1])
    await orm_update_capacity(session, message.from_user.id, new_c)

    await message.answer(f"Разрядность изменилась, текущая: {new_c}")


@user_router.message(Command('change_quan'))
async def update_c(message: Message, session: AsyncSession):
    new_q = int(message.text.split()[-1])
    await orm_update_quantity(session, message.from_user.id, new_q)

    await message.answer(f"Разрядность изменилась, текущая: {new_q}")


@user_router.message(Command('get_values'))
async def get_v(message: Message, session: AsyncSession):
    values = await orm_get_values(session, message.from_user.id)

    print(values)
    await message.answer(f"Значения: {values}")


@user_router.callback_query(F.data == 'info_btn')
async def info_cmd(callback: CallbackQuery):
    markup = get_markup(1, 'backward')
    await callback.message.edit_text(text=LEXICON_RU['info'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню информации")


@user_router.callback_query(F.data == 'settings_btn')
async def settings_cmd(callback: CallbackQuery, session: AsyncSession):
    values = await orm_get_values(session, callback.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1]),
                                                                reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню настроек")


@user_router.callback_query(F.data == 'capacity_btn')
async def capacity_choice(callback: CallbackQuery, session: AsyncSession):
    # current_capacity = await orm_get_capacity()
    markup = get_markup(2, cap_1='1', cap_10='10', cap_100='100',
                        cap_1000='1000', cap_10000='10000')
    await callback.message.edit_text(text=LEXICON_RU['capacity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает разрядность чисел')


@user_router.callback_query(F.data.in_(['cap_1', 'cap_10', 'cap_100',
                                        'cap_1000', 'cap_10000']))
async def capacity_done(callback: CallbackQuery, session: AsyncSession):
    await orm_update_capacity(session, callback.from_user.id, int(callback.data.split('_')[-1]))
    values = await orm_get_values(session, callback.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1]),
                                                                reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} выбрал разрядность и находится в меню настроек")


@user_router.callback_query(F.data == 'quantity_btn')
async def quantity_choice(callback: CallbackQuery, session: AsyncSession):
    markup = get_markup(3, **generate_dict_quan())
    await callback.message.edit_text(text=LEXICON_RU['quantity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает кол-во действий')


@user_router.callback_query(F.data.in_(map(edit_call, range(2, 19))))
async def quantity_done(callback: CallbackQuery, session: AsyncSession):
    values = await orm_get_values(session, callback.from_user.id)
    await orm_update_quantity(session, callback.from_user.id, int(callback.data.split('_')[-1]))
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1]),
                                                                reply_markup=markup)
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