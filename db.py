from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rainmind.db")
engine = create_async_engine(DATABASE_URL, echo = False)
session_maker = async_sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

Base = declarative_base()

async def get_session():
    async with session_maker() as session:
        yield session