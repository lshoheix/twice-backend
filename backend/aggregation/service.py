"""Aggregation service: participation, retention."""
from datetime import datetime, timedelta

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event_log import EventLog


async def get_participation(
    session: AsyncSession, from_date: datetime, to_date: datetime
) -> dict:
    # target_users: distinct accounts with SERVICE_VISIT between from/to
    target_q = (
        select(distinct(EventLog.account_id))
        .where(EventLog.event_type == "SERVICE_VISIT")
        .where(EventLog.occurred_at >= from_date)
        .where(EventLog.occurred_at <= to_date)
    )
    target_result = await session.execute(target_q)
    target_users = len(target_result.scalars().all())

    # finished_users: distinct accounts with FINISH between from/to
    finished_q = (
        select(distinct(EventLog.account_id))
        .where(EventLog.event_type == "FINISH")
        .where(EventLog.occurred_at >= from_date)
        .where(EventLog.occurred_at <= to_date)
    )
    finished_result = await session.execute(finished_q)
    finished_users = len(finished_result.scalars().all())

    participation_rate = finished_users / target_users if target_users else 0.0
    return {
        "target_users": target_users,
        "finished_users": finished_users,
        "participation_rate": round(participation_rate, 4),
    }


async def get_retention_4w(
    session: AsyncSession, anchor_date: datetime
) -> dict:
    # 4 weekly buckets ending at anchor_date (inclusive). anchor_end = start of next day.
    anchor_end = anchor_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    total_users_set = set()
    retained_account_ids = None

    for w in range(4):
        start_w = anchor_end - timedelta(days=7 * (w + 1))
        end_w = anchor_end - timedelta(days=7 * w)

        q = (
            select(distinct(EventLog.account_id))
            .where(EventLog.event_type == "SERVICE_VISIT")
            .where(EventLog.occurred_at >= start_w)
            .where(EventLog.occurred_at < end_w)
        )
        result = await session.execute(q)
        week_accounts = set(result.scalars().all())
        total_users_set |= week_accounts
        if retained_account_ids is None:
            retained_account_ids = week_accounts.copy()
        else:
            retained_account_ids &= week_accounts

    total_users = len(total_users_set)
    retained_users = len(retained_account_ids) if retained_account_ids is not None else 0
    retention_rate = retained_users / total_users if total_users else 0.0
    return {
        "total_users": total_users,
        "retained_users": retained_users,
        "retention_rate": round(retention_rate, 4),
    }
