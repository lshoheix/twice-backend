"""Engagement 도메인 Service 구현체. Mock 데이터 사용."""
import uuid
from datetime import datetime, timedelta
from .models import ServiceAccessRequest, ServiceAccessResponse
from .service_interface import EngagementServiceInterface

# Mock: 서비스 접속 이력 — 30명 (user-01 ~ user-30), 인당 1~2회 접속
def _build_mock_accesses() -> list[dict]:
    now = datetime.utcnow()
    out = []
    for i in range(1, 31):
        user_id = f"user-{i:02d}"
        # 첫 접속: 5~35일 전 분산 (4주 지속률 계산용)
        days_ago = 5 + (i % 31)
        out.append({
            "access_id": f"acc-{i:03d}-1",
            "user_id": user_id,
            "accessed_at": now - timedelta(days=days_ago),
        })
        # 약 절반은 최근 1~3일 내 재접속 (지속률용)
        if i % 2 == 0:
            out.append({
                "access_id": f"acc-{i:03d}-2",
                "user_id": user_id,
                "accessed_at": now - timedelta(days=i % 3, hours=12 - i % 12),
            })
    return out


_MOCK_ACCESSES = _build_mock_accesses()


class EngagementServiceImpl(EngagementServiceInterface):
    """서비스 접속 기록 구현체 (Mock)."""

    def __init__(self) -> None:
        self._accesses: list[dict] = [dict(a) for a in _MOCK_ACCESSES]

    def record_access(self, request: ServiceAccessRequest) -> ServiceAccessResponse:
        accessed_at = datetime.utcnow()
        access_id = f"acc-{uuid.uuid4().hex[:8]}"
        self._accesses.append({
            "access_id": access_id,
            "user_id": request.user_id,
            "accessed_at": accessed_at,
        })
        return ServiceAccessResponse(
            user_id=request.user_id,
            accessed_at=accessed_at,
            access_id=access_id,
        )

    def get_all_accesses(self) -> list[dict]:
        """Aggregation 등에서 참여율 계산용으로 사용 (Mock)."""
        return list(self._accesses)
