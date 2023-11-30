from aiogram import types
from aiogram.filters import CommandObject
from aiogram.utils.keyboard import InlineKeyboardButton

async def help_command(message: types.Message, command: CommandObject):
    """

    :param message:
    :param command:
    :return:
    """
    if command.args:
        from bot.main import bot_commands
        for cmd in bot_commands:
            if cmd[0] == command.args:
                return await message.answer(f'{cmd[0]} - {cmd[1]}\n\n{cmd[2]}')
        else:
            return await message.answer('Kommanda ne naydena')
    return await message.answer('Pomosh i spravka o bote\n'
                                'dlya togo chtobi poluchit info o komnade /help <komanda>'
                                )


async def help_func(message: types.Message):
    """

    :param message:
    :return:
    """
    return await message.answer(
        'help func'
    )


async def call_help_func(call: types.CallbackQuery):
    """

    :param message:
    :return:
    """
    return await call.message.edit_text(
        'help func',
        reply_markup=call.message.reply_markup.inline_keyboard.append([
            InlineKeyboardButton(text='nazad', callback_data='clear')
        ])
    )


async def clear_call_help_func(call: types.CallbackQuery):
    await call.message.edit_text('help func')

