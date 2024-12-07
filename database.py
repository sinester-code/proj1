from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
from sqlalchemy import select
# Конфигурация базы данных
DATABASE_URL = "sqlite+aiosqlite:///./subscribe.db"  # SQLite файл в текущей папке
from aiogram import Bot
import asyncio

# Создание движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание базового класса для моделей
Base = declarative_base()

# Создание фабрики сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Функция для инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для получения сессии
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
