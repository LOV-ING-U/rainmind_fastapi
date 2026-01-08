import asyncio, json
from redis_operation import *

async def main():
    redis = await redis()

    while True:
        payload = await alarm_dequeue(redis, datetime.now(tzinfo = ZoneInfo("Asia/Seoul")))

        if payload is not None:
            print("[Alarm]", json.loads(payload))
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())