from datetime import datetime, timedelta
from exception.exceptions import *
from repository.schedule_repository import *
from repository.outbox_repository import *

import json

async def createSchedule(session: AsyncSession, title: str, location: str, startAt: datetime, endAt: datetime):
    if startAt >= endAt:
        raise EndStartReversedException("should be : start time < end time")
    
    # transaction
    async with session.begin():
        schedule = await save(
            session, Schedule(title = title, location = location, startAt = startAt, endAt = endAt)
        )

        payload = json.dumps({
            "scheduleId": schedule.id,
            "title": schedule.title,
            "location": schedule.location,
            "startAt": schedule.startAt.isoformat(),
            "endAt": schedule.endAt.isoformat(),
            "alarmAt": (schedule.startAt - timedelta(minutes = 30)).isoformat()
        }, ensure_ascii = False)

        await save(session, Outbox(
            scheduleId = schedule.id,
            payload = payload,
            status = "PENDING",
            createdAt = datetime.now()
        ))

    return schedule.id

async def deleteSchedule(session: AsyncSession, schedule_id: int):
    # transaction
    async with session.begin():
        schedule = await findById(session, schedule_id)

        if schedule is None:
            return ScheduleNotFoundException()
        
        await delete(session, schedule)
    