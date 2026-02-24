"""Engagement 도메인: 서비스 접속 이벤트 모델."""
from datetime import datetime
from pydantic import BaseModel, Field


class ServiceAccessRequest(BaseModel):
    """서비스 접속 기록 요청."""
    user_id: str = Field(..., description="수강생(사용자) ID")


class ServiceAccessResponse(BaseModel):
    """서비스 접속 기록 응답."""
    user_id: str = Field(..., description="수강생 ID")
    accessed_at: datetime = Field(..., description="접속 시각")
    access_id: str = Field(..., description="접속 이벤트 ID")
