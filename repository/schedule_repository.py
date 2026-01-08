from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from entity.models import *

async def save(session: AsyncSession, schedule: Schedule) -> Schedule:
    session.add(schedule)
    await session.flush()
    return schedule

async def findById(session: AsyncSession, schedule_id: int) -> Schedule | None:
    item = await session.execute(select(Schedule).where(Schedule.Id == schedule_id))
    return item.scalar_one_or_none()

async def delete(session: AsyncSession, schedule: Schedule):
    await session.delete(schedule)
