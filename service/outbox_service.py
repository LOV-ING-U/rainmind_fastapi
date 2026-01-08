from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from repository.outbox_repository import *
from datetime import datetime
from redis_operation import *

async def enqAfterCommit(session: AsyncSession, redis: Redis):
    pendings = await findByStatus(session, "PENDING")

    if not pendings:
        return
    
    for event in pendings:
        await alarm_enqueue(redis, event.payload, event.alarmAt)
    
    for event in pendings:
        event.status = "SENT"

    await session.commit()