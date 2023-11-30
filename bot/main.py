import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware, ConstI18nMiddleware, FSMI18nMiddleware, I18nMiddleware
from aioredis import Redis
# from sqlalchemy import URL

from bot.config import token, LOCALES_DIR, I18N_DOMAIN


from db import create_async_engine, get_session_maker
from language_middleware import setup_middleware

redis = Redis(
    host=os.getenv('REDIS_HOST') or '127.0.0.1',
    password=os.getenv('REDIS_PASSWORD') or None,
    username=os.getenv('REDIS_USER') or None,
)

storage = RedisStorage(redis=redis)

dp = Dispatcher(storage=storage)

setup_middleware(dp)

async def main() -> None:
    from bot.commands import register_user_commands, BotCommand, bot_commands
    logging.basicConfig(level=logging.DEBUG)

    cmd_for_bot = []
    for cmd in bot_commands:
        cmd_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))


    # i18n = I18n(path=LOCALES_DIR, default_locale='ru', domain=I18N_DOMAIN)
    # i18n_middleware = SimpleI18nMiddleware(i18n=i18n)
    # i18n_middleware = ConstI18nMiddleware(i18n=i18n, locale='ru')
    # i18n_middleware = FSMI18nMiddleware(i18n=i18n)
    # i18n_middleware = I18nMiddleware(i18n=i18n)
    bot = Bot(token=token)
    await bot.set_my_commands(commands=cmd_for_bot)
    register_user_commands(dp)

    postgres_url = os.getenv('db_async')

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)

    # await proceed_schemas(async_engine, BaseModel.metadata)

    await dp.start_polling(bot, session_maker=session_maker)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot Stopped')
