"""
FastAPI 애플리케이션 엔트리포인트.
PM-LSH-1: 시작 시 config.load_env()를 1회 호출하여 환경 변수를 로드한다.
Controller는 Service 인터페이스만 의존하므로, 구현체 주입은 여기서 수행한다.
"""
from config.env import load_env

load_env()

from fastapi import Depends, FastAPI, HTTPException

from kakao_authentication.controller import get_kakao_auth_service, router as kakao_router
from kakao_authentication.models import OAuthLinkResponse
from kakao_authentication.service_interface import KakaoAuthServiceInterface
from kakao_authentication.service_impl import KakaoAuthServiceImpl

app = FastAPI(title="Kakao Authentication Backend")
app.include_router(kakao_router, prefix="/kakao-authentication", tags=["kakao-authentication"])

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

