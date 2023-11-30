
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter
from sqlalchemy import select, CursorResult

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from bot.db.models import User, Unautorized_User


class RegisterCheck(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        session_maker: sessionmaker = data['session_maker']
        async with session_maker() as session:
            async with session.begin():
                session: AsyncSession
                result = await session.execute(select(Unautorized_User).where(Unautorized_User.user_id == event.from_user.id))
                result: CursorResult
                user = result.one_or_none()

                if user is not None:
                    pass
                else:
                    user = Unautorized_User(
                        user_id=event.from_user.id,
                        username=event.from_user.username,
                        fullname=event.from_user.full_name
                    )

                    await session.merge(user)
                    if isinstance(event, Message):
                        await event.answer('Ti uspeshno zaregistrirovan!')
                    else:
                        await event.message.answer('Ti uspeshno zaregistrirovan!')

        return await handler(event, data)

