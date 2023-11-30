from functools import wraps

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from bot.commands.get_pharmacies import get_pharmacy
from bot.commands.login_handlers import start
from bot.db.models import get_user, save_pharmacy

from bot.main import dp

class PharmacyStates(StatesGroup):
    """

    """

    waiting_for_inn = State()
    waiting_for_name = State()
    waiting_for_district = State()
    waiting_for_FIO_director = State()
    waiting_for_phone = State()


async def create_pharmacy(message: types.Message, session_maker: sessionmaker, state: FSMContext) -> None:
    user = await get_user(user_id=message.from_user.id, session=session_maker)
    if user:
        await state.set_state(PharmacyStates.waiting_for_inn)
        kb = [
            [KeyboardButton(text='cancel')],
        ]

        keyboard = ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True, resize_keyboard=True)
        await message.answer('send inn', reply_markup=keyboard)


def cancel_keyboard():
    kb = [
        [KeyboardButton(text='cancel')],
        [KeyboardButton(text='back')],
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True, resize_keyboard=True)
    return keyboard


async def get_inn(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    if message.text == 'cancel' or message.text == 'back':
        await state.clear()
        return await start(message, session_maker)
    cancel_board = cancel_keyboard()
    await state.update_data(inn=message.text)
    await state.set_state(PharmacyStates.waiting_for_name)
    await message.answer('send name', reply_markup=cancel_board)


async def get_name(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    cancel_board = cancel_keyboard()
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker=session_maker)

    if message.text == 'back':
        await state.set_state(PharmacyStates.waiting_for_inn)
        await message.answer('send inn', reply_markup=cancel_board)
        return
    await state.update_data(name=message.text)
    await state.set_state(PharmacyStates.waiting_for_district)
    await message.answer('send district', reply_markup=cancel_board)


async def get_district(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    cancel_board = cancel_keyboard()
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker=session_maker)

    if message.text == 'back':
        await state.set_state(PharmacyStates.waiting_for_name)
        await message.answer('send name', reply_markup=cancel_board)
        return
    await state.update_data(district=message.text)
    await state.set_state(PharmacyStates.waiting_for_FIO_director)
    await message.answer('send FIO director', reply_markup=cancel_board)


async def get_fio_director(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    cancel_board = cancel_keyboard()
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker=session_maker, )

    if message.text == 'back':
        await state.set_state(PharmacyStates.waiting_for_district)
        await message.answer('send district', reply_markup=cancel_board)
        return
    await state.update_data(fio_director=message.text)
    await state.set_state(PharmacyStates.waiting_for_phone)
    await message.answer('send phone', reply_markup=cancel_board)


async def get_phone(message: types.Message, session_maker: sessionmaker, state: FSMContext) -> None:

    cancel_board = cancel_keyboard()
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker=session_maker, )

    if message.text == 'back':
        await state.set_state(PharmacyStates.waiting_for_FIO_director)
        await message.answer('send FIO director', reply_markup=cancel_board)
        return
    await state.update_data(phone=message.text)
    data = await state.get_data()
    await save_pharmacy(data=data, session=session_maker, message=message)
    await state.clear()
    await message.answer('saved!')
    await start(session_maker=session_maker, message=message)

