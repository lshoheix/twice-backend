"""Kakao 인증 API 요청/응답 모델."""
from typing import Optional

from pydantic import BaseModel, Field


class OAuthLinkResponse(BaseModel):
    """PM-LSH-2: 인증 URL 생성 API 응답. auth_url, client_id, redirect_uri, response_type 포함."""
    auth_url: str = Field(..., description="Kakao OAuth 인증 URL")
    client_id: str = Field(..., description="Kakao REST API 키(client_id)")
    redirect_uri: str = Field(..., description="인증 후 리다이렉트 URI")
    response_type: str = Field(default="code", description="OAuth response_type")


class TokenAndUserResponse(BaseModel):
    """PM-LSH-3 + PM-LSH-4: 액세스 토큰 발급 및 사용자 정보 통합 응답."""
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    refresh_token: Optional[str] = Field(None, description="리프레시 토큰")
    expires_in: Optional[int] = Field(None, description="액세스 토큰 만료 시간(초)")
    refresh_token_expires_in: Optional[int] = Field(None, description="리프레시 토큰 만료 시간(초)")
    user: Optional["KakaoUserInfo"] = Field(None, description="Kakao 사용자 정보")


class KakaoUserInfo(BaseModel):
    """PM-LSH-4: Kakao 사용자 정보 (id, 닉네임, 이메일 등)."""
    id: int = Field(..., description="Kakao 사용자 ID")
    nickname: Optional[str] = Field(None, description="닉네임")
    email: Optional[str] = Field(None, description="이메일 (동의 시)")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")


TokenAndUserResponse.model_rebuild()
