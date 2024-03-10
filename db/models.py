from sqlalchemy import BigInteger, DateTime, SmallInteger, String, Float, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    capacity: Mapped[int] = mapped_column(SmallInteger)
    quantity: Mapped[int] = mapped_column(SmallInteger)
    speed: Mapped[float] = mapped_column(Float)