from aiogram import types

from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardMarkup)

from bot.commands.callback_data import TestCallbackData


async def settings_command(message: types.Message):
    settings_markup = InlineKeyboardBuilder()
    settings_markup.button(
        text='Yandex',
        url='yandex.ru'
    )
    # settings_markup.button(
    #     text='Pay',
    #     pay=True
    # )
    settings_markup.button(
        text='help',
        callback_data=TestCallbackData(text='privet', user_id=message.from_user.id)
    )
    await message.answer('settings', reply_markup=settings_markup.as_markup())


async def settings_callback(call: types.CallbackQuery, callback_data: TestCallbackData):
    await call.message.answer(callback_data.text + ', ' + str(callback_data.user_id))