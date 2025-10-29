# init_db.py
import asyncio
from app.db import engine, Base

async def init_db():
    # создаём таблицы, если ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
