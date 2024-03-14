import logging
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from lexicon.lexicon import LEXICON_RU
from filters.filters import IsAdmin
from keyboards.inline_keyboard import get_markup
from db.requests import orm_get_number_users, orm_get_id_users
from fsm.fsm import FSMMailing


admin_router = Router()
admin_router.message.filter(IsAdmin())

logger = logging.getLogger(__name__)


@admin_router.message(Command('admin'))
async def auth_admin(message: Message):
    markup = get_markup(2, 'number_btn', 'mailing_btn')
    await message.delete()
    await message.answer(LEXICON_RU['start'], reply_markup=markup)


@admin_router.callback_query(F.data == 'number_btn')
async def number_users(callback: CallbackQuery, session: AsyncSession):
    users = await orm_get_number_users(session)
    markup = get_markup(1, 'backward_admin')
    await callback.message.edit_text(LEXICON_RU['number_users'].format(users=users),
                                     reply_markup=markup)


@admin_router.callback_query(F.data == 'mailing_btn')
async def mailing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON_RU['mailing_fill'])
    await state.set_state(FSMMailing.fill_text)


@admin_router.message(StateFilter(FSMMailing.fill_text))
async def mailing_start(message: Message, state: FSMContext, session: AsyncSession):
    markup = get_markup(1, 'backward_admin')
    await message.delete()
    await message.answer(LEXICON_RU['mailing_start'])
    ids = await orm_get_id_users(session)
    users = [int(item) for tuple_item in ids for item in tuple_item]
    receive_users, block_users = 0, 0
    for user in users:
        try:
            await message.bot.send_message(user, message.text)
            receive_users += 1
        except:
            block_users += 1
        await asyncio.sleep(0.4)
    await message.answer(LEXICON_RU['mailing_end'].format(receive_users=receive_users,
                                                          block_users=block_users),
                         reply_markup=markup)
    await state.clear()



@admin_router.callback_query(F.data == 'backward_admin')
async def backward(callback: CallbackQuery):
    markup = get_markup(2, 'number_btn', 'mailing_btn')
    await callback.message.edit_text(LEXICON_RU['start'], reply_markup=markup)