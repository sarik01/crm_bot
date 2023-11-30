from typing import Union
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine as _create_async_engine
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return _create_async_engine(url=url, echo=False, pool_pre_ping=True)


async def proceed_schemas(engine: AsyncEngine, MetaData) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(MetaData.create_all)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
