from typing import Any, Dict

from aiogram import types
from aiogram.utils.i18n import I18nMiddleware, I18n

from bot.config import LOCALES_DIR
from bot.db.models import get_lang as user_lang


async def get_lang(user_id, session):
    user = await user_lang(user_id, session)
    if user:
        return user


class ACLMiddleware(I18nMiddleware):
    async def get_locale(self, event: types.Message, data: Dict[str, Any]) -> str:
        user = event.from_user
        session = data['session_maker']
        user_lang = await get_lang(user.id, session)
        if user_lang is None:
            return user.language_code
        return user_lang


def setup_middleware(dp):
    i18n = I18n(path=LOCALES_DIR)
    i18n = ACLMiddleware(i18n=i18n)
    dp.message.outer_middleware.register(i18n)
