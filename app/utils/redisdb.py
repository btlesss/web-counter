import os
import redis.asyncio as aredis
redis_pool = aredis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=os.getenv("REDIS_PORT", 6379),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    db=0, decode_responses=True,
)


class RedisDB:
    async def __aenter__(self) -> aredis.Redis:
        self._con = aredis.Redis(connection_pool=redis_pool)
        return self._con

    async def __aexit__(self, type, value, traceback):
        await self._con.aclose()