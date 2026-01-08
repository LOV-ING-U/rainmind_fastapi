from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy.orm import declarative_base

db_url = "sqlite+aiosqlite:///./rainmind.db"
engine = create_async_engine(db_url, echo = False)
session_maker = async_sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session