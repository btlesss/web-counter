import redis.asyncio as aredis
from time import time
from dtypes import Group, RedisGroup, Counter, RedisCounter, CounterTimings
from asyncio import gather


async def group_from_redis(redis_group: RedisGroup, db: aredis.Redis) -> Group:
    """Convert Redis group to Group
    (counters ids to counters objects)

    Args:
        redis_group (RedisGroup): group from redis with counters_ids instead of objects
        db (aredis.Redis): redis connection instance
        with_timings (bool): Fill timings Defaults to False.

    Returns:
        Group: group instance with filled counters field
    """
    tasks = []
    for counter_id in redis_group.counters:
        counter_raw = await db.hgetall(f"counter:{counter_id}")
        if counter_raw == {}:
            continue
        counter = RedisCounter(**counter_raw)
        tasks.append(counter_from_redis(counter, db))

    instance = Group(**redis_group.model_dump(exclude=["counters"]))
    instance.counters = await gather(*tasks)
    return instance


async def counter_from_redis(redis_counter: RedisCounter, db: aredis.Redis) -> Counter:
    """Convert Redis counter to Counter
    (fill timings field with values)

    Args:
        redis_counter (RedisCounter): counter from redis without timings
        db (aredis.Redis): redis connection instance

    Returns:
        Counter: counter with filled timings field
    """

    instance = Counter(**redis_counter.model_dump())
    times = {  # minutes from current moment back to 24h, 7 and 30 days
        "per24h": 60 * 24,
        "per7d": 60 * 24 * 7,
        "per30d": 60 * 24 * 30,
    }
    for field, timing in times.items():
        start = time() // 60 - timing  # start time of slice
        times[field] = await db.zcount(f"counter:{instance.id}:values", start, "+inf")

    instance.timings = CounterTimings(**times)
    return instance
