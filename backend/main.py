"""
FastAPI 애플리케이션 엔트리포인트.
PM-LSH-1: 시작 시 config.load_env()를 1회 호출하여 환경 변수를 로드한다.
Controller는 Service 인터페이스만 의존하므로, 구현체 주입은 여기서 수행한다.
"""
import sys
from pathlib import Path

# backend 폴더를 Python 경로에 넣어서, 프로젝트 루트에서 실행해도 import가 동작하도록 함
_backend_dir = Path(__file__).resolve().parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config.env import load_env

load_env()

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from aggregation.router import router as analytics_router
from database import engine
from engagement.router import router as engagement_router
from kakao_authentication.controller import get_kakao_auth_service, router as kakao_router
from kakao_authentication.models import OAuthLinkResponse
from kakao_authentication.service_interface import KakaoAuthServiceInterface
from kakao_authentication.service_impl import KakaoAuthServiceImpl
from models import Base
from quiz.router import router as quiz_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Kakao Authentication Backend", lifespan=lifespan)
app.include_router(kakao_router, prefix="/kakao-authentication", tags=["kakao-authentication"])
app.include_router(engagement_router, prefix="/engagement", tags=["engagement"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Layered Architecture: Controller는 인터페이스만 의존, 구현체는 엔트리포인트에서 주입
app.dependency_overrides[get_kakao_auth_service] = lambda: KakaoAuthServiceImpl()


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
