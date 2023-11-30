from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import select, CursorResult
from sqlalchemy.orm import sessionmaker
from aiogram import types
from bot.db.models import get_user, get_user_phone, Unautorized_User
from aiogram.utils.i18n import gettext as _

class LoginStates(StatesGroup):
    """

    """

    waiting_for_phone = State()
    waiting_for_password = State()


async def start(message: types.Message, session_maker: sessionmaker) -> None:
    user = await get_user(user_id=message.from_user.id, session=session_maker)
    if user:
        menu_builder = ReplyKeyboardBuilder()
        menu_builder.button(
            text='create a pharmacy'
        )
        menu_builder.button(
            text='pharmacies'
        )
        await message.answer('Menu',
                             reply_markup=menu_builder.as_markup(resize_keyboard=True, one_time_keyboard=True,)
                             )
    else:
        menu_builder = ReplyKeyboardBuilder()
        menu_builder.button(
            text=_('ru')
        )
        menu_builder.button(
            text='uz'
        )
        await message.answer('Menu',
                             reply_markup=menu_builder.as_markup(resize_keyboard=True, one_time_keyboard=True,)
                             )


async def selected_lang(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker() as session:
        result = await session.execute(
            select(Unautorized_User).filter(Unautorized_User.user_id == message.from_user.id))
        result: CursorResult
        user = result.scalar()

        if user is not None:
            if message.text == _('ru'):
                user.lang = 'ru'
            else:
                user.lang = 'uz'
        else:
            user = Unautorized_User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                fullname=message.from_user.full_name,
                lang=message.text
            )

            await session.merge(user)

        await session.commit()
    await state.set_state(LoginStates.waiting_for_phone)
    kb = [
        [KeyboardButton(text='send cantact', request_contact=True)],
        [KeyboardButton(text='cancel')],
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True, resize_keyboard=True)

    await message.answer('send cantact',
                         reply_markup=keyboard)


async def get_contact(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    """

    :param message:
    :param state:
    :param session_maker:
    :return:
    """
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker=session_maker)
    if message.text == 'back':
        return await start(message, session_maker)
    phone = message.contact.phone_number
    result = await get_user_phone(phone=phone, session=session_maker, message=message)

    cancel_board = ReplyKeyboardBuilder()

    cancel_board.row(
        KeyboardButton(text='cancel'),
        KeyboardButton(text='back')
    )

    if result:
        await state.update_data(phone=phone)
        await state.set_state(LoginStates.waiting_for_password)

        await message.answer('Ok, now send me password', reply_markup=cancel_board.as_markup(resize_keyboard=True))
    else:
        await message.answer('no, such phone in base', reply_markup=cancel_board.as_markup(resize_keyboard=True))


async def get_password(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    if message.text == 'cancel':
        await state.clear()
        return await start(message, session_maker)
    if message.text == 'back':
        await state.clear()
        return await selected_lang(message, state)
    data = await state.get_data()
    result = await get_user_phone(password=message.text, session=session_maker, message=message,
                                  phone=data.get('phone'))
    if result:
        await state.set_state(LoginStates.waiting_for_password)
        await message.answer('right')
        await state.clear()
        await start(message, session_maker)
    else:
        await message.answer('not right password')





#
# # FSM
#
#
# class PostStates(StatesGroup):
#     """
#
#     """
#
#     waiting_for_select = State()
#     waiting_for_text = State()
#     waiting_for_url = State()
#     waiting_for_budget = State()
#     waiting_for_pr_type = State()
#     waiting_for_price_url = State()
#     waiting_for_price_publication = State()
#     waiting_for_subs_min = State()
#
#
# async def menu_posts(message: types.Message, session_maker: sessionmaker, state: FSMContext) -> None:
#     """
#
#     :param message:
#     :param session:
#     :return:
#     """
#     print('ffff')
#     post_keyboard = InlineKeyboardBuilder()
#
#     async with session_maker() as session:
#         async with session.begin():
#             result = await session.execute(
#                 select(User).where(User.user_id == message.from_user.id).options(selectinload(User.posts)))
#             user = result.scalar()
#             print(user.posts)
#             for post in user.posts:
#                 post_keyboard.button(text=post.text[:20], callback_data='getpost' + str(post.id))
#             post_keyboard.button(text='Create post', callback_data='createpost')
#             post_keyboard.adjust(1)
#             await message.answer('Your Posts', reply_markup=post_keyboard.as_markup())
#             await state.set_state(PostStates.waiting_for_select)
#
#
# async def menu_post_create(message: types.CallbackQuery, state: FSMContext) -> None:
#     """
#
#     :param message:
#     :return:
#     """
#     await state.set_state(PostStates.waiting_for_text)
#
#     await message.message.answer('Send text of new post', reply_markup=cancel_board())
#
#
# async def menu_post_text(message: types.Message, state: FSMContext) -> None:
#     """
#
#     :param message:
#     :param state:
#     :return:
#     """
#     if message.text == 'cancel':
#         await state.clear()
#         return await start(message)
#
#     await state.update_data(post_text=message.text)
#     await state.set_state(PostStates.waiting_for_url)
#     await message.answer('Ok, now send me url', reply_markup=cancel_board())
#
#
# async def menu_post_url(message: types.Message, state: FSMContext) -> None:
#     """
#
#     :param message:
#     :param state:
#     :return:
#     """
#     if message.text == 'cancel':
#         await state.clear()
#         return await start(message)
#
#     if message.text == 'back':
#         await state.set_state(PostStates.waiting_for_text)
#         await message.answer('Send text of new post', reply_markup=cancel_board())
#
#     else:
#         await state.update_data(post_url=message.text)
#         await state.set_state(PostStates.waiting_for_pr_type)
#         rkm_builder = ReplyKeyboardBuilder()
#         rkm_builder.button(text='Oplata po publikaciyam')
#         rkm_builder.button(text='Oplata za perehod publicacii')
#         await message.answer('Teper varian raskrutki', reply_markup=rkm_builder.as_markup(resize_keyboard=True))
#
#
# async def menu_post_get(message: types.Message) -> None:
#     """
#
#     :param message:
#     :return:
#     """
