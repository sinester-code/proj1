from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.future import select
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from aiogram import Bot
from database import get_session
from sqlalchemy.exc import IntegrityError

import config
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)  # id как PRIMARY KEY
    name = Column(String, nullable=False)  # name как VARCHAR (NOT NULL)
    email = Column(String, nullable=False, unique=True)  # email с ограничением UNIQUE
    sub_id = Column(Integer, nullable=False)  # sub_id как INTEGER (NOT NULL)
    tg_id = Column(Integer, nullable=True)  # tg_id как INTEGER, можно NULL
    
    __table_args__ = (
        UniqueConstraint('email', name='_email_uc'),  # Ограничение UNIQUE для email
    )
    
class Subs(Base):
    __tablename__ = "subs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    date_start = Column(String, nullable=False)
    date_end = Column(String, nullable=False)



from database import get_session

async def get_uid_bd(tg_id: int):
    # Получаем сессию
    async for session in get_session():
        # Проверка, существует ли уже tg_id в базе данных
        stmt = select(User.sub_id).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            
            return int(user)
        else:
            return int("нету такого в бд")

async def check_and_add_tg_id(tg_id: int, uid: int):
    # Получаем сессию
    async for session in get_session():
        # Проверка, существует ли уже tg_id в базе данных
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Если tg_id уже существует
            return f"Пользователь с tg_id {tg_id} уже существует."

        # Если tg_id не найден, добавляем нового пользователя с tg_id и uid
        new_user = User(tg_id=tg_id, sub_id=uid, name="123", email=f"asd@{uid}.com")  # Пример, name и email должны быть определены
        session.add(new_user)

        try:
            await session.commit()
            return f"Пользователь с tg_id {tg_id} и uid {uid} успешно добавлен."
        except IntegrityError as e:
            # В случае ошибки, откатываем транзакцию
            await session.rollback()
            return f"Ошибка при добавлении пользователя: {str(e)}"


async def add_subscription(session: AsyncSession, user_id: int, date_start: str, date_end: str):
    sub = Subs(user_id=user_id, date_start=date_start, date_end=date_end)
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub

async def notify_users(session: AsyncSession, bot: Bot, days_before_end: int):
    """Проверяет подписки и уведомляет пользователей и администратора."""
    # Текущая дата
    today = datetime.now().date()

    # Дата, после которой будем отправлять уведомления
    notify_date = today + timedelta(days=days_before_end)

    # Выполняем запрос к базе данных
    result = await session.execute(
        select(Subs).where(Subs.date_end == notify_date.isoformat())
    )
    subscriptions = result.scalars().all()

    # Если есть подходящие записи, уведомляем
    for sub in subscriptions:
        # Отправляем уведомление пользователю
        await bot.send_message(
            chat_id=sub.user_id,
            text=f"Ваша подписка истекает {sub.date_end}. Пожалуйста, продлите её, чтобы избежать её отключения!"
        )
        # Отправляем уведомление администратору
        await bot.send_message(
            chat_id=config.ADMINS[0],
            text=f"Подписка пользователя {sub.user_id} истекает {sub.date_end}."
        )


async def get_subscription(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Subs).where(Subs.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    return subscription