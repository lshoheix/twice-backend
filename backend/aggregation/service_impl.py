"""Aggregation 도메인 Service 구현체. Mock 데이터 기반 계산."""
from datetime import datetime, timedelta
from typing import Any
from .models import ParticipationRateResponse, Retention4WeeksResponse
from .service_interface import AggregationServiceInterface


class AggregationServiceImpl(AggregationServiceInterface):
    """참여율/4주 지속률 계산 구현체. Engagement/Quiz 서비스 인스턴스를 주입받아 같은 Mock 데이터를 참조."""

    def __init__(
        self,
        engagement_service: Any,
        quiz_service: Any,
    ) -> None:
        self._engagement = engagement_service
        self._quiz = quiz_service

    def get_participation_rate(self) -> ParticipationRateResponse:
        accesses = self._engagement.get_all_accesses()
        sessions = self._quiz.get_all_sessions()
        # 접속한 고유 사용자 수
        unique_accessed = len({a["user_id"] for a in accesses})
        # 퀴즈를 finish한 고유 사용자 수
        def is_finished(s: dict) -> bool:
            state = s.get("state")
            return getattr(state, "value", state) == "finish"
        finished_user_ids = {s["user_id"] for s in sessions if is_finished(s)}
        total_finished_quiz = len(finished_user_ids)
        if unique_accessed == 0:
            rate = 0.0
        else:
            rate = round(100.0 * total_finished_quiz / unique_accessed, 2)
        return ParticipationRateResponse(
            participation_rate=rate,
            total_accessed=unique_accessed,
            total_finished_quiz=total_finished_quiz,
        )

    def get_retention_4weeks(self) -> Retention4WeeksResponse:
        accesses = self._engagement.get_all_accesses()
        # Mock: 4주 전을 기준으로 그 전에 접속한 사용자 수, 그 중 4주 내 다시 접속한 수
        now = datetime.utcnow()
        four_weeks_ago = now - timedelta(weeks=4)
        baseline_user_ids = {a["user_id"] for a in accesses if a["accessed_at"] < four_weeks_ago}
        retained_user_ids = {
            a["user_id"]
            for a in accesses
            if a["accessed_at"] >= four_weeks_ago and a["user_id"] in baseline_user_ids
        }
        baseline_count = len(baseline_user_ids)
        retained_count = len(retained_user_ids)
        if baseline_count == 0:
            retention_4weeks = 0.0
        else:
            retention_4weeks = round(100.0 * retained_count / baseline_count, 2)
        return Retention4WeeksResponse(
            retention_4weeks=retention_4weeks,
            baseline_count=baseline_count,
            retained_count=retained_count,
        )
