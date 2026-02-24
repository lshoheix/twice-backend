"""
FastAPI 애플리케이션 엔트리포인트.
PM-LSH-1: 시작 시 config.load_env()를 1회 호출하여 환경 변수를 로드한다.
Controller는 Service 인터페이스만 의존하므로, 구현체 주입은 여기서 수행한다.
"""
from config.env import load_env

load_env()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from kakao_authentication.controller import get_kakao_auth_service, router as kakao_router
from kakao_authentication.models import OAuthLinkResponse
from kakao_authentication.service_interface import KakaoAuthServiceInterface
from kakao_authentication.service_impl import KakaoAuthServiceImpl

from engagement.controller import get_engagement_service, router as engagement_router
from engagement.service_interface import EngagementServiceInterface
from engagement.service_impl import EngagementServiceImpl

from quiz.controller import get_quiz_service, router as quiz_router
from quiz.service_interface import QuizServiceInterface
from quiz.service_impl import QuizServiceImpl

from aggregation.controller import get_aggregation_service, router as aggregation_router
from aggregation.service_interface import AggregationServiceInterface
from aggregation.service_impl import AggregationServiceImpl

app = FastAPI(title="Kakao Authentication Backend")

# 프론트엔드(다른 origin)에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 특정 origin만 허용하도록 변경 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kakao_router, prefix="/kakao-authentication", tags=["kakao-authentication"])
app.include_router(engagement_router, prefix="/engagement", tags=["engagement"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
app.include_router(aggregation_router, prefix="/aggregation", tags=["aggregation"])

# Layered Architecture: Controller는 인터페이스만 의존, 구현체는 엔트리포인트에서 주입
app.dependency_overrides[get_kakao_auth_service] = lambda: KakaoAuthServiceImpl()

# Engagement / Quiz / Aggregation: Mock 데이터 공유를 위해 동일 인스턴스 주입
_engagement_svc = EngagementServiceImpl()
_quiz_svc = QuizServiceImpl()
_aggregation_svc = AggregationServiceImpl(_engagement_svc, _quiz_svc)
app.dependency_overrides[get_engagement_service] = lambda: _engagement_svc
app.dependency_overrides[get_quiz_service] = lambda: _quiz_svc
app.dependency_overrides[get_aggregation_service] = lambda: _aggregation_svc


@app.get("/", response_model=OAuthLinkResponse)
def root(
    service: KakaoAuthServiceInterface = Depends(get_kakao_auth_service),
) -> OAuthLinkResponse:
    """루트 접속 시 Kakao OAuth 인증 URL(auth_url, client_id, redirect_uri, response_type)을 반환한다."""
    try:
        return service.get_oauth_link()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# --- MVP 시퀀스 (1~6): 한 번에 접속 → 퀴즈 시작 → 퀴즈 완료(점수 저장)까지 실행 ---
from typing import Optional
from pydantic import BaseModel, Field


class MVPSequenceRequest(BaseModel):
    """MVP 1~6 시퀀스 요청 (Mock 플로우 테스트)."""
    user_id: str = Field(..., description="수강생 ID")
    quiz_id: str = Field(default="quiz-1", description="퀴즈 ID")
    score: float = Field(default=80.0, ge=0, le=100, description="완료 시 점수")
    improvement_rate: Optional[float] = Field(default=None, description="개선율")
    evaluation: Optional[str] = Field(default=None, description="Evaluation")


@app.post("/mvp/sequence")
def mvp_sequence(
    body: MVPSequenceRequest,
    engagement_svc: EngagementServiceInterface = Depends(get_engagement_service),
    quiz_svc: QuizServiceInterface = Depends(get_quiz_service),
):
    """MVP 1~6: 서비스 접속 → 퀴즈 시작 → 퀴즈 완료(상태 finish + 점수 저장). Mock 데이터로 동작."""
    from engagement.models import ServiceAccessRequest
    from quiz.models import QuizStartRequest, QuizFinishRequest

    # 1. 수강생 서비스 접속
    access = engagement_svc.record_access(ServiceAccessRequest(user_id=body.user_id))
    # 2. 퀴즈 시작 (상태 start 저장)
    start = quiz_svc.start_quiz(QuizStartRequest(user_id=body.user_id, quiz_id=body.quiz_id))
    # 4~6. 퀴즈 완료 (상태 finish 저장, 점수/개선율/Evaluation 저장)
    finish = quiz_svc.finish_quiz(
        QuizFinishRequest(
            session_id=start.session_id,
            score=body.score,
            improvement_rate=body.improvement_rate,
            evaluation=body.evaluation,
        )
    )
    return {
        "step1_access": access.model_dump(),
        "step2_start": start.model_dump(),
        "step4_5_6_finish": finish.model_dump(),
    }

