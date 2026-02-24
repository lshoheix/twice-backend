"""Quiz API: start, progress, complete, abandon."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from quiz import service as quiz_service

router = APIRouter()


class StartBody(BaseModel):
    account_id: str
    quiz_id: str
    difficulty_level: str


class StartResponse(BaseModel):
    attempt_id: str


class ProgressBody(BaseModel):
    account_id: str
    attempt_id: str


class CompleteBody(BaseModel):
    account_id: str
    attempt_id: str
    score: int


class AbandonBody(BaseModel):
    account_id: str
    attempt_id: str


@router.post("/start", response_model=StartResponse)
async def post_start(body: StartBody, db: AsyncSession = Depends(get_db)) -> StartResponse:
    if body.difficulty_level not in ("LOW", "MID", "HIGH"):
        raise HTTPException(status_code=400, detail="invalid difficulty_level")
    attempt_id = await quiz_service.start_attempt(
        db, body.account_id, body.quiz_id, body.difficulty_level
    )
    return StartResponse(attempt_id=attempt_id)


@router.post("/progress")
async def post_progress(body: ProgressBody, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await quiz_service.progress_attempt(db, body.attempt_id)
        return {"ok": True}
    except LookupError:
        raise HTTPException(status_code=404, detail="attempt not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complete")
async def post_complete(body: CompleteBody, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await quiz_service.complete_attempt(db, body.attempt_id, body.score)
        return {"ok": True}
    except LookupError:
        raise HTTPException(status_code=404, detail="attempt not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/abandon")
async def post_abandon(body: AbandonBody, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await quiz_service.abandon_attempt(db, body.attempt_id)
        return {"ok": True}
    except LookupError:
        raise HTTPException(status_code=404, detail="attempt not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
async def get_history(
    account_id: str = Query(..., description="계정 ID"),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await quiz_service.list_attempts_by_account(db, account_id)
