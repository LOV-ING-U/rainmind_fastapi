import pytest
import httpx
from main import app
import json
import asyncio

from db import *
from redis_operation import redis as get_redis
from redis_operation import ZSET_KEY, alarm_dequeue
from entity.models import *
from sqlalchemy import select
from service.outbox_service import enqAfterCommit

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest.mark.anyio
async def test():
    await init_db()

    r = await get_redis()

    now = datetime.now(ZoneInfo("Asia/Seoul"))
    startAt = now + timedelta(minutes = 31)
    endAt = startAt + timedelta(minutes = 30)

    transport = httpx.ASGITransport(app = app)

    async with httpx.AsyncClient(transport = transport, base_url = "http://test") as client:
        response = await client.post(
            "/schedules",
            json = {
                "title": "meeting",
                "location": "SNU",
                "startAt": startAt.isoformat(),
                "endAt": endAt.isoformat()
            }
        )
    
    # check status
    assert response.status_code == 201, response.text
    schedule_id = response.json()["scheduleId"]
    print("generated schedule id : " + str(schedule_id))

    # automatic test version
    outbox_sent = False
    queue_empty = False

    time_limit = asyncio.get_event_loop().time() + 10.0

    while asyncio.get_event_loop().time() < time_limit:
        async with session_maker() as session:
            result = await session.execute(
                select(Outbox.status).where(Outbox.scheduleId == schedule_id)
            )

            statuses = []
            for row in result.all():
                statuses.append(row[0])

            if "SENT" in statuses:
                outbox_sent = True

        zset_count = await r.zcard(ZSET_KEY)
        if zset_count == 0:
            queue_empty = True

        if outbox_sent and queue_empty:
            break

        await asyncio.sleep(0.2)

    await r.aclose()

    assert outbox_sent, "event_publisher failed"
    assert queue_empty, "worker failed"

    # non - automatic test version
    # async with session_maker() as session:
    #     result = await session.execute(
    #         select(Outbox).where(
    #             Outbox.scheduleId == schedule_id,
    #             Outbox.status == "PENDING"
    #         )
    #     )

    #     outbox = result.scalars().all()
    #     assert outbox, "Cannot check schedule in Outbox Table"

    #     # redis enqueue
    #     await enqAfterCommit(session, r)

    # enq_count = await r.zcard(ZSET_KEY)
    # assert enq_count >= 1, "Not enqueued in redis"

    # # alarm pop test
    # pop_time = now + timedelta(minutes = 5)
    # payload = await alarm_dequeue(r, pop_time)
    # assert payload is not None, "Failed deque in redis"

    # print("[Alarm]", json.loads(payload))
    # await r.aclose()