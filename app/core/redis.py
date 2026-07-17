import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    health_check_interval=30,
)

async def connect_redis():
    try:
        await redis_client.ping()
        print(" Redis Connected")
    except Exception as e:
        print(f" Redis Connection Failed : {e}")

async def disconnect_redis():
    await redis_client.close()