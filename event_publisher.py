import asyncio
from db import *
from redis_operation import *
from service.outbox_service import *

async def main():
    redis = await redis()

    while True:
        async with session_maker() as session:
            await enqAfterCommit(session, redis)

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())