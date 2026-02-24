"""Analytics API: participation, retention."""
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from aggregation.service import get_participation, get_retention_4w
from database import get_db

router = APIRouter()


@router.get("/participation")
async def get_participation_route(
    from_: date = Query(..., alias="from", description="YYYY-MM-DD"),
    to: date = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from_dt = datetime.combine(from_, datetime.min.time())
    to_end = datetime.combine(to, datetime.max.time())
    return await get_participation(db, from_dt, to_end)


@router.get("/retention/4w")
async def get_retention_4w_route(
    anchor_date: date = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    anchor = datetime.combine(anchor_date, datetime.min.time())
    return await get_retention_4w(db, anchor)
