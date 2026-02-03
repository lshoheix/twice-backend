"""
PM-LSH-2, PM-LSH-3, PM-LSH-4: Kakao 인증 Service 구현체.
환경 변수(.env) 기반으로 client_id, redirect_uri를 로드하며 코드에 하드코딩하지 않는다.
"""
import os
from typing import Optional
from urllib.parse import urlencode

import httpx

from kakao_authentication.models import (
    KakaoUserInfo,
    OAuthLinkResponse,
    TokenAndUserResponse,
)
from kakao_authentication.service_interface import KakaoAuthServiceInterface

# Kakao OAuth 상수 (엔드포인트 URL만 고정, client_id/redirect_uri는 env)
# 인가 코드 방식 사용 시 response_type은 반드시 "code" (Kakao 지원 유일 값)
KAKAO_AUTHORIZE_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_ME_URL = "https://kapi.kakao.com/v2/user/me"
RESPONSE_TYPE_CODE = "code"


class KakaoAuthServiceImpl(KakaoAuthServiceInterface):
    """Kakao 인증 Service 구현체. 환경 변수에서 설정을 읽는다."""

    def __init__(self) -> None:
        self._client_id = os.environ.get("KAKAO_CLIENT_ID", "").strip()
        # redirect_uri는 쿼리 제거(인가 코드 방식에서 Kakao가 요구하는 형식)
        raw = os.environ.get("KAKAO_REDIRECT_URI", "").strip()
        self._redirect_uri = raw.split("?")[0] if raw else ""

    def _ensure_config(self) -> None:
        if not self._client_id or not self._redirect_uri:
            raise ValueError(
                "KAKAO_CLIENT_ID와 KAKAO_REDIRECT_URI가 .env에 설정되어 있어야 합니다."
            )

    def get_oauth_link(self) -> OAuthLinkResponse:
        """PM-LSH-2: Kakao OAuth 인증 URL 생성. response_type=code(인가 코드 방식)로 고정."""
        self._ensure_config()
        # Kakao: 지원하지 않는 응답 유형 오류 방지 — response_type은 반드시 "code"
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }
        auth_url = f"{KAKAO_AUTHORIZE_URL}?{urlencode(params)}"
        return OAuthLinkResponse(
            auth_url=auth_url,
            client_id=self._client_id,
            redirect_uri=self._redirect_uri,
            response_type=RESPONSE_TYPE_CODE,
        )

    def exchange_code_for_token_and_user(self, code: str) -> TokenAndUserResponse:
        """PM-LSH-3: 인가 코드로 토큰 발급 후, PM-LSH-4: 액세스 토큰으로 사용자 정보 조회하여 통합 반환."""
        self._ensure_config()
        if not (code and code.strip()):
            raise ValueError("인가 코드(code)가 필요합니다.")

        # PM-LSH-3: 토큰 발급
        token_data = self._request_token(code.strip())
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("액세스 토큰을 받지 못했습니다.")

        # PM-LSH-4: 발급된 액세스 토큰으로 사용자 정보 조회
        user_info = self._fetch_user_info(access_token)

        return TokenAndUserResponse(
            access_token=access_token,
            token_type=token_data.get("token_type", "bearer"),
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
            refresh_token_expires_in=token_data.get("refresh_token_expires_in"),
            user=user_info,
        )

    def _request_token(self, code: str) -> dict:
        """Kakao 토큰 엔드포인트에 인가 코드로 토큰 요청."""
        payload = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "code": code,
        }
        with httpx.Client() as client:
            resp = client.post(
                KAKAO_TOKEN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if resp.status_code != 200:
            body = resp.text
            try:
                err = resp.json()
                body = err.get("error_description", body)
            except Exception:
                pass
            raise ValueError(f"토큰 발급 실패: {body}")

        return resp.json()

    def _fetch_user_info(self, access_token: str) -> Optional[KakaoUserInfo]:
        """PM-LSH-4: 액세스 토큰으로 Kakao 사용자 정보 조회."""
        with httpx.Client() as client:
            resp = client.get(
                KAKAO_USER_ME_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if resp.status_code != 200:
            return None

        data = resp.json()
        kakao_account = data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        return KakaoUserInfo(
            id=data.get("id", 0),
            nickname=profile.get("nickname"),
            email=kakao_account.get("email"),
            profile_image_url=profile.get("profile_image_url"),
        )
