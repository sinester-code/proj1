import asyncio
from database import engine, Base

async def init_db():
    async with engine.begin() as conn:
        # Удаление таблиц (если требуется, например, для тестов)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Создание таблиц
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
