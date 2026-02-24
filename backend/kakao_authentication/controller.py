"""
PM-LSH-2, PM-LSH-3: Kakao 인증 Controller.
Service 인터페이스에만 의존하며, 환경 변수/URL 구성 로직은 다루지 않고 요청 전달 및 응답 반환만 수행한다.
구현체 주입은 main(엔트리포인트)에서 dependency_overrides로 수행한다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from engagement.service import get_or_create_account_by_kakao_id
from kakao_authentication.models import OAuthLinkResponse, TokenAndUserResponse
from kakao_authentication.service_interface import KakaoAuthServiceInterface


def get_kakao_auth_service() -> KakaoAuthServiceInterface:
    """DI: 구현체는 main에서 주입되며, Controller는 인터페이스 타입만 사용한다."""
    raise NotImplementedError("get_kakao_auth_service는 main에서 구현체로 override되어야 합니다.")


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
    response_model=TokenAndUserResponse,
    summary="인가 코드로 액세스 토큰 및 사용자 정보 발급",
    description="PM-LSH-3, PM-LSH-4: 인가 코드(code)로 액세스 토큰을 발급하고, 해당 토큰으로 Kakao 사용자 정보를 조회하여 함께 반환합니다.",
)
async def request_access_token_after_redirection(
    code: str = Query(..., description="Kakao 인증 후 리다이렉트된 인가 코드"),
    service: KakaoAuthServiceInterface = Depends(get_kakao_auth_service),
    db: AsyncSession = Depends(get_db),
) -> TokenAndUserResponse:
    try:
        resp = service.exchange_code_for_token_and_user(code=code)
        account_id = None
        if resp.user:
            account_id = await get_or_create_account_by_kakao_id(db, resp.user.id)
        return TokenAndUserResponse(
            access_token=resp.access_token,
            token_type=resp.token_type,
            refresh_token=resp.refresh_token,
            expires_in=resp.expires_in,
            refresh_token_expires_in=resp.refresh_token_expires_in,
            user=resp.user,
            account_id=account_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
