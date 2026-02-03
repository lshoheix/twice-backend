# Kakao Authentication Backend (FastAPI)

PM-LSH-1 ~ PM-LSH-4 전략에 따른 Kakao OAuth 인증 백엔드입니다.

## 요구 사항

- Python 3.10+
- `.env` 파일 (프로젝트 루트)

## 환경 변수 (.env)

```env
KAKAO_CLIENT_ID=your_rest_api_key
KAKAO_REDIRECT_URI=http://localhost:8000/callback
```

카카오 개발자 콘솔에서 REST API 키와 Redirect URI를 등록한 뒤 위 값으로 설정하세요.

## 설치 및 실행

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

- API 문서: http://localhost:8000/docs
- Health: `GET /health`
- OAuth URL 발급: `GET /kakao-authentication/request-oauth-link`
- 토큰·사용자 정보: `GET /kakao-authentication/request-access-token-after-redirection?code=...`

## 구조 (Layered Architecture)

- **config**: 환경 변수 로딩 (`load_env`) — PM-LSH-1
- **kakao_authentication**
  - **controller**: HTTP 요청/응답만 담당, Service 인터페이스에만 의존
  - **service_interface**: Kakao 인증 Service 추상 인터페이스
  - **service_impl**: Kakao API 호출 및 env 기반 설정
  - **models**: 요청/응답 Pydantic 모델

구현체 주입은 `main.py`의 `app.dependency_overrides`에서 수행합니다.
