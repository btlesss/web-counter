from fastapi import APIRouter, Body, Path, Query
from fastapi.responses import JSONResponse

from utils import RedisDB, counter_from_redis
from dtypes import RedisCounter, Counter, NewCounter, OperationSuccess

from random import randint
from time import time

router = APIRouter(prefix="/counter", tags=["counters"])


@router.post("/", description="create new counter", status_code=201)
async def create_counter(
    new_counter: NewCounter = Body(
        examples=[NewCounter(name="Some human-readable name")]
    ),
) -> Counter:
    counter = RedisCounter(**new_counter.model_dump())
    counter.generate_id()

    async with RedisDB() as db:
        # generate id that doesnt exists
        while await db.get(f"counter:{counter.id}") is not None:
            counter.generate_id()

        await db.hset(f"counter:{counter.id}", mapping=counter.model_dump())
    
    counter = Counter(**counter.model_dump())
    return counter


@router.get("/{counter_id}", description="get counter value", tags=["counters"])
async def get_counter(
    counter_id: str = Path(title="id of counter", examples=["kumanju"])
) -> Counter:
    async with RedisDB() as db:
        counter_raw = await db.hgetall(f"counter:{counter_id}")
        if counter_raw == {}:
            return JSONResponse({"details": "Counter not found"}, 404)
        counter = await counter_from_redis(RedisCounter(**counter_raw), db)

    return counter


@router.patch("/{counter_id}", description="set counter name")
async def set_counter_name(
    counter_id: str = Path(title="id of counter", examples=["kumanju"]),
    new_name: str = Query(description="new human-readable name of counter"),
) -> OperationSuccess:
    async with RedisDB() as db:
        counter_raw = await db.hgetall(f"counter:{counter_id}")
        if counter_raw == {}:
            return JSONResponse({"details": "Counter not found"}, 404)

        counter = RedisCounter(**counter_raw)
        counter.name = new_name

        await db.hset(f"counter:{counter.id}", mapping=counter.model_dump())


@router.put(
    "/{counter_id}",
    description="Increment counter or set new value",
)
async def increment_counter(
    counter_id: str = Path(title="id of counter", examples=["kumanju"]),
    unique_id: str = Query(
        default=None,
        max_length=64,
        description="any information that identifies a unique item to be counted\nif not specified - counts are non-unique",
    ),
) -> Counter:
    async with RedisDB() as db:
        counter_raw = await db.hgetall(f"counter:{counter_id}")
        if counter_raw == {}:
            return JSONResponse({"details": "Counter not found"}, 404)

        counter = RedisCounter(**counter_raw)

        if not unique_id:
            unique_id = randint(10**7,10**10)
        added_count = await db.zadd(f"counter:{counter.id}:values", {unique_id: int(time()//60)}, nx=True)
        counter.value += added_count
        
        await db.hset(f"counter:{counter.id}", mapping=counter.model_dump())
        
        counter = await counter_from_redis(counter, db)

    return counter
