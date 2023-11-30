from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cancel_board() -> ReplyKeyboardMarkup:
    """

    :return:
    """

    rk_builder = ReplyKeyboardBuilder()
    rk_builder.button(text='cancel')
    rk_builder.button(text='back')
    return rk_builder.as_markup(resize_keyboard=True)