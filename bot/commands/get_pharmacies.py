from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy import select, ScalarResult
from sqlalchemy.orm import sessionmaker, selectinload

from bot.commands import create_act
from bot.commands.login_handlers import start
from bot.db.models import User, add_to_cart, get_medicine, get_ordered_medicine, update_leftover_in_order


class PharmacyGetStates(StatesGroup):
    """

    """

    waiting_for_pharmacy = State()
    waiting_for_select = State()
    waiting_for_orders = State()
    waiting_for_leftover = State()
    waiting_for_balance = State()
    waiting_for_quantity = State()
    waiting_for_add_another_to_cart = State()
    waiting_for_select_medicine = State()
    waiting_for_select_write_left = State()
    waiting_for_select_for_medicine_left = State()



async def pharmacies(message: types.Message, session_maker: sessionmaker, state: FSMContext) -> None:
    async with session_maker() as session:
        result = await session.execute(
            select(User).filter(User.user_id == message.from_user.id).options(selectinload(User.pharmacies)))
        user = result.scalar()
        kb_generator = [[KeyboardButton(text=f'{x.name}-{x.district}')] for x in user.pharmacies]

        kb = ReplyKeyboardMarkup(keyboard=kb_generator, resize_keyboard=True, row_width=1, one_time_keyboard=True)
        await message.answer('pharmacies', reply_markup=kb)
        await state.set_state(PharmacyGetStates.waiting_for_pharmacy)


async def get_pharmacy(message: types.Message, state: FSMContext) -> None:
    pharmacy, district = message.text.split('-')
    print(district)
    await state.update_data(pharmacy=pharmacy)
    await state.update_data(district=district)
    kb_generator = [
        [KeyboardButton(text='orders')],
        [KeyboardButton(text='leftover')],
        [KeyboardButton(text='balance')],
    ]

    kb = ReplyKeyboardMarkup(keyboard=kb_generator, resize_keyboard=True, row_width=1, one_time_keyboard=True)
    await message.answer('select module', reply_markup=kb)
    await state.set_state(PharmacyGetStates.waiting_for_select)


async def select_module(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    text = message.text
    if text == 'orders':
        await state.set_state(PharmacyGetStates.waiting_for_orders)
        await message.answer('write medicine')
    elif text == 'leftover':
        medicine = await get_ordered_medicine(data=await state.get_data(), session=session_maker)
        if medicine:
            await state.set_state(PharmacyGetStates.waiting_for_select_medicine)
            await message.answer('now select medicine', reply_markup=medicine)
            await state.set_state(PharmacyGetStates.waiting_for_leftover)
    elif text == 'balance':
        await create_act(message=message, state=state, session_maker=session_maker)


async def order(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(med_name=message.text)
    medicine = await get_medicine(data=await state.get_data(), session=session_maker)
    if medicine:
        await state.set_state(PharmacyGetStates.waiting_for_select_medicine)
        await message.answer('now select medicine', reply_markup=medicine)
    else:
        await message.answer('no such medicine')


async def select_for_medicine(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    if message.text == 'back':
        await state.set_state(PharmacyGetStates.waiting_for_orders)
        await message.answer('write medicine', reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(med_name=message.text)
        await state.set_state(PharmacyGetStates.waiting_for_quantity)
        await message.answer('now send me quantity')


async def quantity(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    await state.update_data(med_quantity=message.text)
    await add_to_cart(session=session_maker, data=await state.get_data())
    kb_generator = [
        [KeyboardButton(text='add another one')],
        [KeyboardButton(text='enough')],
    ]

    kb = ReplyKeyboardMarkup(keyboard=kb_generator, resize_keyboard=True, row_width=1, one_time_keyboard=True)
    await state.set_state(PharmacyGetStates.waiting_for_add_another_to_cart)
    await message.answer('now, choose one of em', reply_markup=kb)


async def add_another_to_cart(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    if message.text == 'add another one':
        await state.set_state(PharmacyGetStates.waiting_for_orders)
        await message.answer('write medicine')
    else:
        await state.clear()
        await start(session_maker=session_maker, message=message)


async def leftover(message: types.Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(medicine=message.text)
    await state.set_state(PharmacyGetStates.waiting_for_select_for_medicine_left)
    await message.answer('now write leftover')


async def select_for_medicine_left(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:

    pass


async def write_left(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    await state.update_data(left=message.text)
    left = await update_leftover_in_order(session=session_maker, data=await state.get_data())
    if left:
        await message.answer('left updated!')
        await state.clear()
        await start(message, session_maker)
