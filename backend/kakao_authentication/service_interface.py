"""PM-LSH-2, PM-LSH-3, PM-LSH-4: Kakao 인증 Service 인터페이스. Controller는 이 인터페이스에만 의존한다."""
from abc import ABC, abstractmethod

from kakao_authentication.models import KakaoUserInfo, OAuthLinkResponse, TokenAndUserResponse


class KakaoAuthServiceInterface(ABC):
    """Kakao 인증 Service 추상 인터페이스. 구현체에 직접 의존하지 않는다."""

    @abstractmethod
    def get_oauth_link(self) -> OAuthLinkResponse:
        """PM-LSH-2: Kakao OAuth 인증 URL을 생성하여 반환한다."""
        ...

    @abstractmethod
    def exchange_code_for_token_and_user(self, code: str) -> TokenAndUserResponse:
        """PM-LSH-3 + PM-LSH-4: 인가 코드로 액세스 토큰을 발급받고, 해당 토큰으로 사용자 정보를 조회하여 함께 반환한다."""
        ...
