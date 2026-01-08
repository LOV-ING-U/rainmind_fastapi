from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from entity.models import *

async def findByStatus(session: AsyncSession, state: str) -> list[Outbox]:
    items = await session.execute(select(Outbox).where(Outbox.status == state))
    return items.scalars().all()

async def save(session: AsyncSession, event: Outbox) -> Outbox:
    session.add(event)
    await session.flush()
    return event