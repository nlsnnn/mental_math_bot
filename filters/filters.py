from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from services.services import edit_call


class SpeedFilter(BaseFilter):
    async def __call__(self, message: Message):
        return (0.5 <= float(message.text) <= 10.5) and float(message.text) % 0.5 == 0


class IsDigit(BaseFilter):
    async def __call__(self, message: Message):
        if message.text.startswith('+') or message.text.startswith('-'):
            return message.text[1:].isdigit()
        return message.text.isdigit()


class IsTrueAnswer(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        data = await state.get_data()
        true_answer = data.get('true_answer')
        return int(message.text) == true_answer


class QuantityFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        values = list(map(edit_call, range(2, 19)))
        return callback.data in values


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, admin_id: str):
        return int(admin_id) == message.from_user.id