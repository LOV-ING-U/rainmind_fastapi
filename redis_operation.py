from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from redis.asyncio import Redis

ZSET_KEY = "alarm:queue"

def time_to_float(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo = ZoneInfo("Asia/Seoul"))
    return dt.timestamp()

def alarm_at(st: datetime) -> datetime:
    return st - timedelta(minutes = 30)

LUA_POP_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
            
    local items = redis.call('ZRANGEBYSCORE', key, '-inf', now, 'LIMIT', 0, 1)
    if (#items == 0) then
        return nil
    end
            
    redis.call('ZREM', key, items[1])
    return items[1]
"""

async def redis() -> Redis:
    return Redis(host = "localhost", port = 6379, decode_responses = True)

async def alarm_enqueue(redis: Redis, payload: str, alarmAt: datetime):
    score = alarmAt.replace(tzinfo = ZoneInfo("Asia/Seoul")).timestamp()
    await redis.zadd(ZSET_KEY, {payload: score})

async def alarm_dequeue(redis: Redis, now: datetime) -> str | None:
    now_float = now.replace(tzinfo = ZoneInfo("Asia/Seoul")).timestamp()
    payload = await redis.eval(LUA_POP_SCRIPT, 1, ZSET_KEY, now_float)
    return payload