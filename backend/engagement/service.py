"""Engagement service: ensure account, record visit."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.account import Account
from models.event_log import EventLog

SERVICE_VISIT = "SERVICE_VISIT"


async def get_or_create_account_by_kakao_id(session: AsyncSession, kakao_id: int) -> str:
    result = await session.execute(select(Account).where(Account.kakao_id == kakao_id))
    account = result.scalars().first()
    if account:
        return account.id
    account = Account(id=str(uuid.uuid4()), kakao_id=kakao_id)
    session.add(account)
    await session.flush()
    return account.id


async def ensure_account_exists(session: AsyncSession, account_id: str) -> None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    if result.scalars().first() is not None:
        return
    account = Account(id=account_id)
    session.add(account)
    await session.flush()


async def record_visit(session: AsyncSession, account_id: str) -> None:
    await ensure_account_exists(session, account_id)
    log = EventLog(account_id=account_id, event_type=SERVICE_VISIT)
    session.add(log)
    await session.flush()
