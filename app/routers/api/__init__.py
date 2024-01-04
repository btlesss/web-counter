from fastapi import APIRouter
from . import counters, groups

from dtypes import OperationSuccess

router = APIRouter(prefix="/api")

router.include_router(counters.router)
router.include_router(groups.router)


@router.get("/ping")
async def ping() -> OperationSuccess:
    return OperationSuccess()