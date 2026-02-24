"""
PM-LSH-2, PM-LSH-3: Kakao 인증 Controller.
Service 인터페이스에만 의존하며, 환경 변수/URL 구성 로직은 다루지 않고 요청 전달 및 응답 반환만 수행한다.
구현체 주입은 main(엔트리포인트)에서 dependency_overrides로 수행한다.
카카오 콜백:
- Accept: application/json 이면 200 + JSON (access_token, refresh_token, user) 반환. 프론트 fetch용.
- 그 외(브라우저 리다이렉트)면 302로 프론트 /login/callback?access_token=... 로 리다이렉트.
"""
import os
from urllib.parse import urlencode, quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from kakao_authentication.models import OAuthLinkResponse, TokenAndUserResponse
from kakao_authentication.service_interface import KakaoAuthServiceInterface


def get_kakao_auth_service() -> KakaoAuthServiceInterface:
    """DI: 구현체는 main에서 주입되며, Controller는 인터페이스 타입만 사용한다."""
    raise NotImplementedError("get_kakao_auth_service는 main에서 구현체로 override되어야 합니다.")


def _frontend_callback_base_url() -> str:
    """프론트엔드 base URL (trailing slash 제거). 기본값: http://localhost:3000"""
    base = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000").strip()
    return base.rstrip("/")


router = APIRouter()


@router.get(
    "/request-oauth-link",
    response_model=OAuthLinkResponse,
    summary="Kakao OAuth 인증 URL 발급",
    description="PM-LSH-2: 사용자가 Kakao 인증 요청 시 인증 URL을 반환합니다.",
)
def request_oauth_link(
    service: KakaoAuthServiceInterface = Depends(get_kakao_auth_service),
) -> OAuthLinkResponse:
    try:
        return service.get_oauth_link()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/request-access-token-after-redirection",
    summary="카카오 OAuth 콜백: Accept에 따라 200 JSON 또는 302 리다이렉트",
    description="Accept: application/json 이면 200 + JSON(access_token, refresh_token, user). 그 외면 302로 FRONTEND_BASE_URL/login/callback?access_token=... 로 리다이렉트.",
)
def request_access_token_after_redirection(
    request: Request,
    code: str = Query(..., description="Kakao 인증 후 리다이렉트된 인가 코드"),
    service: KakaoAuthServiceInterface = Depends(get_kakao_auth_service),
):
    accept = request.headers.get("accept", "") or ""
    wants_json = "application/json" in accept
    print(f"[kakao_callback] request wants_json={wants_json} code_len={len(code)}")

    try:
        data = service.exchange_code_for_token_and_user(code=code)
    except ValueError as e:
        print(f"[kakao_callback] token exchange failed: {e}")
        if wants_json:
            raise HTTPException(status_code=400, detail=str(e))
        frontend_base = _frontend_callback_base_url()
        callback_path = f"{frontend_base}/login/callback"
        error_url = f"{callback_path}?error={quote(str(e))}"
        print(f"[kakao_callback] redirect (error) -> {error_url[:120]}")
        return RedirectResponse(url=error_url, status_code=302)

    if wants_json:
        print(f"[kakao_callback] returning 200 JSON user_id={data.user.id if data.user else None}")
        return data

    frontend_base = _frontend_callback_base_url()
    callback_path = f"{frontend_base}/login/callback"
    params = {"access_token": data.access_token}
    if data.refresh_token:
        params["refresh_token"] = data.refresh_token
    if data.user is not None:
        params["user_id"] = str(data.user.id)
    redirect_url = f"{callback_path}?{urlencode(params)}"
    print(f"[kakao_callback] redirect (success) -> {redirect_url}")
    print(f"[kakao_callback] user_id={params.get('user_id')}")
    return RedirectResponse(url=redirect_url, status_code=302)
