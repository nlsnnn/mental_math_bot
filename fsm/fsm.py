from aiogram.fsm.state import State, StatesGroup


class FSMSettings(StatesGroup):
    fill_speed = State()


class FSMArithmetic(StatesGroup):
    fill_answer = State()


class FSMMailing(StatesGroup):
    fill_text = State()