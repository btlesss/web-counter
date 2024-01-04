from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils import RedisDB, group_from_redis
from dtypes import RedisCounter, Counter, RedisGroup, Group

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    tags=["user interface"]
)

@router.get("/g/{group_id}", response_class=HTMLResponse)
async def view_group(request: Request, group_id: str):
    async with RedisDB() as db:
        group_raw = await db.hgetall(f"group:{group_id}")
        if group_raw is None:
            group = Group(name="Group not found")
        else:
            group = await group_from_redis(RedisGroup(**group_raw), db)
    
    return templates.TemplateResponse(name="group.html", context={"request": request, "group":group})

@router.get("/count/{counter_id}", response_class=HTMLResponse, tags=["user interface"])
async def view_counter(request: Request, counter_id: str):
    return templates.TemplateResponse(name="counter.html", context={"request": request})