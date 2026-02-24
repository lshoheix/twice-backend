"""Quiz 도메인: 퀴즈 상태(start/finish), 점수(개선율, Evaluation) 모델."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class QuizState(str, Enum):
    START = "start"
    FINISH = "finish"


class QuizStartRequest(BaseModel):
    """퀴즈 시작 요청 (MVP 2)."""
    user_id: str = Field(..., description="수강생 ID")
    quiz_id: str = Field(..., description="퀴즈 ID")


class QuizStartResponse(BaseModel):
    """퀴즈 시작 응답."""
    session_id: str = Field(..., description="퀴즈 세션 ID")
    user_id: str = Field(..., description="수강생 ID")
    quiz_id: str = Field(..., description="퀴즈 ID")
    state: QuizState = Field(default=QuizState.START)
    started_at: datetime = Field(..., description="시작 시각")


class QuizFinishRequest(BaseModel):
    """퀴즈 완료 요청 (MVP 4~6). finish 시에만 점수 저장."""
    session_id: str = Field(..., description="퀴즈 세션 ID")
    score: float = Field(..., ge=0, le=100, description="점수 (0~100)")
    improvement_rate: Optional[float] = Field(None, description="개선율")
    evaluation: Optional[str] = Field(None, description="Evaluation 평가")


class QuizFinishResponse(BaseModel):
    """퀴즈 완료 응답."""
    session_id: str = Field(..., description="세션 ID")
    user_id: str = Field(..., description="수강생 ID")
    quiz_id: str = Field(..., description="퀴즈 ID")
    state: QuizState = Field(default=QuizState.FINISH)
    started_at: datetime = Field(..., description="시작 시각")
    finished_at: datetime = Field(..., description="완료 시각")
    score: float = Field(..., description="점수")
    improvement_rate: Optional[float] = None
    evaluation: Optional[str] = None
