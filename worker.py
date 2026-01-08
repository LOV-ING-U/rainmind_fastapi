import asyncio, json
from redis_operation import *

from zoneinfo import ZoneInfo
from datetime import datetime

async def main():
    redis = await redis()

    while True:
        payload = await alarm_dequeue(redis, datetime.now(ZoneInfo("Asia/Seoul")))

        if payload is not None:
            print("[Alarm]", json.loads(payload))
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())