"""Quiz service: start, progress, complete, abandon."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event_log import EventLog
from models.quiz_attempt import QuizAttempt

VALID_STATUS_TRANSITIONS = {
    "START": ["IN_PROGRESS", "FINISH", "ABANDONED"],
    "IN_PROGRESS": ["ABANDONED", "FINISH"],
    "ABANDONED": [],
    "FINISH": [],
}


async def start_attempt(
    session: AsyncSession, account_id: str, quiz_id: str, difficulty_level: str
) -> str:
    attempt = QuizAttempt(
        account_id=account_id,
        quiz_id=quiz_id,
        difficulty_level=difficulty_level,
        status="START",
    )
    session.add(attempt)
    await session.flush()
    return attempt.id


async def get_attempt(session: AsyncSession, attempt_id: str) -> QuizAttempt | None:
    result = await session.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
    return result.scalars().first()


def _check_transition(current: str, new: str) -> None:
    allowed = VALID_STATUS_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise ValueError(f"Invalid status transition from {current} to {new}")


async def progress_attempt(session: AsyncSession, attempt_id: str) -> None:
    attempt = await get_attempt(session, attempt_id)
    if attempt is None:
        raise LookupError("attempt not found")
    _check_transition(attempt.status, "IN_PROGRESS")
    attempt.status = "IN_PROGRESS"
    await session.flush()


async def complete_attempt(session: AsyncSession, attempt_id: str, score: int) -> None:
    attempt = await get_attempt(session, attempt_id)
    if attempt is None:
        raise LookupError("attempt not found")
    _check_transition(attempt.status, "FINISH")
    attempt.status = "FINISH"
    attempt.score = score
    attempt.finished_at = datetime.utcnow()
    await session.flush()
    # Log FINISH event for analytics
    log = EventLog(
        account_id=attempt.account_id,
        event_type="FINISH",
        occurred_at=attempt.finished_at,
    )
    session.add(log)
    await session.flush()


async def abandon_attempt(session: AsyncSession, attempt_id: str) -> None:
    attempt = await get_attempt(session, attempt_id)
    if attempt is None:
        raise LookupError("attempt not found")
    _check_transition(attempt.status, "ABANDONED")
    attempt.status = "ABANDONED"
    attempt.finished_at = datetime.utcnow()
    await session.flush()


async def list_attempts_by_account(
    session: AsyncSession, account_id: str
) -> list[dict]:
    result = await session.execute(
        select(QuizAttempt)
        .where(QuizAttempt.account_id == account_id)
        .order_by(QuizAttempt.created_at.desc())
    )
    attempts = result.scalars().all()
    return [
        {
            "id": a.id,
            "quiz_id": a.quiz_id,
            "difficulty_level": a.difficulty_level,
            "status": a.status,
            "score": a.score,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "finished_at": a.finished_at.isoformat() if a.finished_at else None,
        }
        for a in attempts
    ]
