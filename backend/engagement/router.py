"""Engagement API: visit."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from engagement.service import record_visit

router = APIRouter()


class VisitBody(BaseModel):
    account_id: str


class VisitResponse(BaseModel):
    ok: bool = True


@router.post("/visit", response_model=VisitResponse)
async def post_visit(body: VisitBody, db: AsyncSession = Depends(get_db)) -> VisitResponse:
    await record_visit(db, body.account_id)
    return VisitResponse()
