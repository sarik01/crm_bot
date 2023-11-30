__all__ = ['register_user_commands', 'BotCommand', 'bot_commands']

from aiogram import Router
from aiogram.filters import Command

from bot.commands.callback_data import TestCallbackData
from bot.commands.create_act_of_reconciliation import create_act
from bot.commands.create_pharmacy import create_pharmacy, get_inn, PharmacyStates, get_name, get_district, \
    get_fio_director, get_phone
from bot.commands.get_pharmacies import pharmacies, get_pharmacy, PharmacyGetStates, select_module, order, quantity, \
    add_another_to_cart, select_for_medicine, leftover, select_for_medicine_left, write_left
from bot.commands.login_handlers import (start, get_contact,
                                         LoginStates, get_contact, selected_lang, get_password
                                         )
from bot.commands.bot_commands import bot_commands
from aiogram.types import BotCommand
from bot.commands.help import help_command, help_func, call_help_func, clear_call_help_func
from aiogram import F
from bot.commands.settings import settings_command, settings_callback
from aiogram.utils.i18n import lazy_gettext as _


def register_user_commands(router: Router) -> None:
    router.message.register(start, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(start, F.text == 'Start')
    router.message.register(help_func, F.text == 'Pomosh')
    router.message.register(settings_command, F.text == 'settings')



    # FSM Login
    router.message.register(selected_lang, F.text == _('ru'))
    router.message.register(selected_lang, F.text == 'uz')
    router.message.register(get_contact, LoginStates.waiting_for_phone)
    router.message.register(get_password, LoginStates.waiting_for_password)

    # Pharmacy create

    router.message.register(create_pharmacy, F.text == 'create a pharmacy')
    router.message.register(get_inn, PharmacyStates.waiting_for_inn)
    router.message.register(get_name, PharmacyStates.waiting_for_name)
    router.message.register(get_district, PharmacyStates.waiting_for_district)
    router.message.register(get_fio_director, PharmacyStates.waiting_for_FIO_director)
    router.message.register(get_phone, PharmacyStates.waiting_for_phone)
    router.message.register(pharmacies, F.text == 'pharmacies')
    # router.message.register(get_pharmacy, F.text == 'pizdec5')

    # FSM GET Pharmacy

    router.message.register(get_pharmacy, PharmacyGetStates.waiting_for_pharmacy)
    router.message.register(select_module, PharmacyGetStates.waiting_for_select)
    router.message.register(order, PharmacyGetStates.waiting_for_orders)
    router.message.register(quantity, PharmacyGetStates.waiting_for_quantity)
    router.message.register(add_another_to_cart, PharmacyGetStates.waiting_for_add_another_to_cart)
    router.message.register(select_for_medicine, PharmacyGetStates.waiting_for_select_medicine)
    router.message.register(leftover, PharmacyGetStates.waiting_for_leftover)
    router.message.register(select_for_medicine_left, PharmacyGetStates.waiting_for_select_write_left)
    router.message.register(write_left, PharmacyGetStates.waiting_for_select_for_medicine_left)
    # router.message.register(get_pharmacy, PharmacyGetStates.waiting_for_pharmacy)
