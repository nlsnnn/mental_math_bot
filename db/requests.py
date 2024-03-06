from os import getenv
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from db.models import User, Base
from config_data.config import Config, create_config

config: Config = create_config('.env')

engine = create_async_engine(config.db.sql_url, echo=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def orm_add_user(
        session: AsyncSession,
        tg_id: int,
        name: str | None = None,
        capacity: int = 1,
        quantity: int = 2
):
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(tg_id=tg_id, name=name, capacity=capacity, quantity=quantity)
        )
        await session.commit()


async def orm_get_values(
        session: AsyncSession,
        tg_id: int
):
    query = select(User.capacity, User.quantity).where(User.tg_id == tg_id)
    result = await session.execute(query)

    print("!!!!!!!!!!!!!", result)
    return result.all()


async def orm_get_capacity(
        session: AsyncSession,
        tg_id: int
):
    query = select(User.capacity).where(User.tg_id == tg_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_quantity(
        session: AsyncSession,
        tg_id: int
):
    query = select(User.quantity).where(User.tg_id == tg_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_capacity(
        session: AsyncSession,
        tg_id: int,
        new_capacity: int
):
    query = (update(User).where(User.tg_id == tg_id).values(capacity=new_capacity))
    await session.execute(query)
    await session.commit()


async def orm_update_quantity(
        session: AsyncSession,
        tg_id: int,
        new_quantity: int
):
    query = (update(User).where(User.tg_id == tg_id).values(quantity=new_quantity))
    await session.execute(query)
    await session.commit()