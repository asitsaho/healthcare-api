from fastapi import APIRouter
from sqlalchemy import text

from healthcare_api.api.deps import DbSession

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(db: DbSession) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
