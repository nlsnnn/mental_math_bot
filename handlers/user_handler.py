import logging
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from filters.filters import QuantityFilter, SpeedFilter, IsDigit, IsTrueAnswer
from lexicon.lexicon import LEXICON_RU
from keyboards.inline_keyboard import get_markup
from fsm.fsm import FSMArithmetic, FSMSettings
from services.services import generate_numbers, generate_dict_quan
from db.requests import (orm_add_user, orm_get_values, orm_update_speed,
                         orm_update_capacity, orm_update_quantity, orm_get_date_created)

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
        quantity=2,
        speed=1
    )

    markup = get_markup(2, 'start_btn', 'settings_btn', 'info_btn')
    await message.answer(text=LEXICON_RU['/start'], reply_markup=markup)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@user_router.callback_query(F.data == 'info_btn')
async def info_cmd(callback: CallbackQuery, session: AsyncSession):
    markup = get_markup(1, 'backward')
    date = await orm_get_date_created(session, callback.from_user.id)
    await callback.message.edit_text(text=LEXICON_RU['info'].format(date=date),
                                     reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню информации")


@user_router.callback_query(F.data == 'settings_btn')
async def settings_cmd(callback: CallbackQuery, session: AsyncSession):
    values = await orm_get_values(session, callback.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'speed_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1],
                                                                        speed=values[0][2]),
                                                                reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} в меню настроек")


@user_router.callback_query(F.data == 'capacity_btn')
async def capacity_choice(callback: CallbackQuery):
    markup = get_markup(2, cap_1='1', cap_10='10', cap_100='100',
                        cap_1000='1000', cap_10000='10000')
    await callback.message.edit_text(text=LEXICON_RU['capacity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает разрядность чисел')


@user_router.callback_query(F.data.in_(['cap_1', 'cap_10', 'cap_100',
                                        'cap_1000', 'cap_10000']))
async def capacity_done(callback: CallbackQuery, session: AsyncSession):
    await orm_update_capacity(session, callback.from_user.id, int(callback.data.split('_')[-1]))
    values = await orm_get_values(session, callback.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'speed_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1],
                                                                        speed=values[0][2]),
                                                                reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} выбрал разрядность и находится в меню настроек")


@user_router.callback_query(F.data == 'quantity_btn')
async def quantity_choice(callback: CallbackQuery):
    quan = generate_dict_quan()
    markup = get_markup(3, **quan)
    await callback.message.edit_text(text=LEXICON_RU['quantity'], reply_markup=markup)
    logger.info(f'Пользователь {callback.from_user.id} выбирает кол-во действий')


@user_router.callback_query(QuantityFilter())
async def quantity_done(callback: CallbackQuery, session: AsyncSession):
    await orm_update_quantity(session, callback.from_user.id, int(callback.data.split('_')[-1]))
    values = await orm_get_values(session, callback.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'speed_btn', 'backward')
    await callback.message.edit_text(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                                        quantity=values[0][1],
                                                                        speed=values[0][2]),
                                                                reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} выбрал кол-во действий и находится в меню настроек")


@user_router.callback_query(F.data == 'speed_btn')
async def speed_choice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON_RU['speed'])
    await state.set_state(FSMSettings.fill_speed)
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} выбирает скорость")


@user_router.message(StateFilter(FSMSettings.fill_speed), SpeedFilter())
async def speed_done(message: Message, state: FSMContext, session: AsyncSession):
    await orm_update_speed(session, message.from_user.id, message.text)
    values = await orm_get_values(session, message.from_user.id)
    markup = get_markup(2, 'capacity_btn', 'quantity_btn', 'speed_btn', 'backward')
    await message.delete()
    await message.answer(text=LEXICON_RU['settings'].format(capacity=values[0][0],
                                                            quantity=values[0][1],
                                                            speed=values[0][2]),
                                                            reply_markup=markup)
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} выбрал скорость и находится в меню настроек")


@user_router.message(StateFilter(FSMSettings.fill_speed))
async def wrong_speed(message: Message):
    await message.delete()
    await message.answer(LEXICON_RU['speed_wrong'])
    logger.info(f"Пользователь {message.from_user.id} написал некорректную скорость")


@user_router.callback_query(F.data == "start_btn")
async def start_math(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    logger.info(f"Пользователь {callback.from_user.id} запустил логику")
    capacity, quantity, speed = (await orm_get_values(session, callback.from_user.id))[0]
    digits = generate_numbers(quantity, capacity)
    for i in range(5, 0, -1):
        await callback.message.edit_text(
            text=f"<b>Начало через {i}...</b>"
        )
        await asyncio.sleep(0.5)

    for number in digits:
        try:
            await callback.message.edit_text(
                text=f"<b>{number}</b>"
            )
            await asyncio.sleep(speed)
        except TelegramBadRequest:
            continue

    await state.set_state(FSMArithmetic.fill_answer)
    await state.update_data(true_answer=sum(digits))
    await callback.message.edit_text(f"Введите ответ")


@user_router.message(StateFilter(FSMArithmetic.fill_answer), IsDigit(), IsTrueAnswer())
async def send_true_answer(message: Message, state: FSMContext, session: AsyncSession):
    markup = get_markup(1, 'backward')
    await message.delete()
    await message.answer(LEXICON_RU['true_answer'], reply_markup=markup)
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} ввел правильный ответ")


@user_router.message(StateFilter(FSMArithmetic.fill_answer))
async def send_wrong_answer(message: Message):
    markup = get_markup(1, 'backward')
    await message.delete()
    await message.answer(LEXICON_RU['wrong_answer'], reply_markup=markup)
    logger.info(f"Пользователь {message.from_user.id} ввел неправильный ответ")


@user_router.callback_query(F.data == 'backward')
async def backward(callback: CallbackQuery):
    markup = get_markup(2, 'start_btn', 'settings_btn', 'info_btn')
    await callback.message.edit_text(text=LEXICON_RU['/start'], reply_markup=markup)
    logger.info(f"Пользователь {callback.from_user.id} вернулся в меню")