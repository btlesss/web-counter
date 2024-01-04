from fastapi import APIRouter, Body, Path
from fastapi.responses import JSONResponse

from utils import RedisDB, group_from_redis
from dtypes import RedisGroup, Group, NewGroup, OperationSuccess

router = APIRouter(prefix="/group", tags=["groups"])


@router.post("/", description="create new group", status_code=201)
async def create_group(
    new_group: NewGroup = Body(
        examples=[
            NewGroup(name="Some human-readable name", counters=["kumanju"]).model_dump()
        ]
    )
) -> Group:
    new_group = RedisGroup(**new_group.model_dump())
    new_group.generate_id()

    async with RedisDB() as db:
        # generate id that doesnt exists
        while await db.get(f"group:{new_group.id}") is not None:
            new_group.generate_id()

        await db.hset(
            f"group:{new_group.id}", mapping=new_group.model_dump(mode="json")
        )

        new_group = await group_from_redis(new_group, db)
    print(new_group)
    return new_group


@router.delete("/{group_id}", description="delete group")
async def delete_group(
    group_id: str = Path(title="id of group", examples=["limabux"])
) -> OperationSuccess:
    async with RedisDB() as db:
        n = await db.delete(f"group:{group_id}")
        if n == 0:
            return JSONResponse({"details": "Group not found"}, 404)
    return OperationSuccess()


@router.delete(
    "/{group_id}/{counter_id}",
    description="remove counter from group",
)
async def delete_counter_from_group(
    group_id: str = Path(title="id of group", examples=["limabux"]),
    counter_id: str = Path(title="id of counter", examples=["limabux"]),
) -> OperationSuccess:
    async with RedisDB() as db:
        group_raw = await db.hgetall(f"group:{group_id}")
        if group_raw == {}:
            return JSONResponse({"details": "Group not found"}, 404)

        group = Group(**group_raw)
        if counter_id not in group.counters:
            return JSONResponse({"details": "Counter not in group"}, 404)

        group.counters.remove(counter_id)

        await db.hset(f"group:{group.id}", mapping=group.model_dump(mode="json"))
    return OperationSuccess()
