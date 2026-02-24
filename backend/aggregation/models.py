"""Aggregation 도메인: 참여율, 4주 지속률 모델."""
from pydantic import BaseModel, Field


class ParticipationRateResponse(BaseModel):
    """참여율 응답 (MVP 9)."""
    participation_rate: float = Field(..., ge=0, le=100, description="참여율 (%)")
    total_accessed: int = Field(..., description="서비스 접속한 수강생 수")
    total_finished_quiz: int = Field(..., description="퀴즈를 완료한 수강생 수")


class Retention4WeeksResponse(BaseModel):
    """4주 지속률 응답 (MVP 9)."""
    retention_4weeks: float = Field(..., ge=0, le=100, description="4주 지속률 (%)")
    baseline_count: int = Field(..., description="기준 기간 접속 수")
    retained_count: int = Field(..., description="4주 후에도 참여한 수")
