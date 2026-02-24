# Kakao Authentication Backend (FastAPI)

PM-LSH-1 ~ PM-LSH-4 전략에 따른 Kakao OAuth 인증 백엔드입니다.

## 요구 사항

- Python 3.10+
- `.env` 파일 (프로젝트 루트)

## 환경 변수 (.env)

```env
KAKAO_CLIENT_ID=your_rest_api_key
KAKAO_REDIRECT_URI=http://localhost:8000/kakao-authentication/request-access-token-after-redirection
FRONTEND_BASE_URL=http://localhost:3000
```

- **KAKAO_REDIRECT_URI**: 카카오 로그인 후 리다이렉트될 백엔드 URL (위 예시처럼 콜백 경로 포함).
- **FRONTEND_BASE_URL**: 토큰 발급 후 302 리다이렉트할 프론트엔드 주소. 개발 시 `http://localhost:3000`, 운영 시 실제 프론트 도메인.

카카오 개발자 콘솔에는 `KAKAO_REDIRECT_URI`와 동일한 값을 Redirect URI로 등록하세요.

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

---

## 도메인 구성 (Engagement / Quiz / Aggregation)

### 도메인 관계

- **User** → **Engagement** (서비스 접속)
- **Engagement** → **Quiz** (상태 저장 start/finish, 점수 저장은 finish 시만)
- **Quiz** → **Aggregation** (참여율, 4주 지속률)

### API (Mock 데이터 기반, 1~6번)

| 단계 | 설명 | API |
|------|------|-----|
| 1 | 수강생 서비스 접속 | `POST /engagement/access` (body: `user_id`) |
| 2 | 퀴즈 시작 (상태 start 저장) | `POST /quiz/start` (body: `user_id`, `quiz_id`) |
| 3 | start만 있고 finish 없으면 중도포기 | (별도 API 없음, 상태로 구분) |
| 4~6 | 퀴즈 완료 (상태 finish + 점수/개선율/Evaluation 저장) | `POST /quiz/finish` (body: `session_id`, `score`, `improvement_rate`, `evaluation`) |
| 9 | 참여율 / 4주 지속률 | `GET /aggregation/participation-rate`, `GET /aggregation/retention-4weeks` |

### MVP 시퀀스 한 번에 실행 (1→2→4~6)

- `POST /mvp/sequence`  
  - body: `user_id`, `quiz_id`(선택), `score`, `improvement_rate`, `evaluation`(선택)  
  - 동작: 접속 기록 → 퀴즈 시작 → 퀴즈 완료(점수 저장) 후 응답 반환

---

## 웹에서 기능 확인하는 방법

서버 실행 후 (`uvicorn main:app --reload --port 8000`):

### 1) Swagger UI로 한곳에서 모두 확인 (권장)

브라우저에서 **http://localhost:8000/docs** 를 연다.

- **engagement**: 서비스 접속 기록 API
- **quiz**: 퀴즈 시작 / 퀴즈 완료 API
- **aggregation**: 참여율, 4주 지속률 API
- **mvp**: MVP 시퀀스(접속→시작→완료 한 번에) API

각 API를 펼친 뒤 **Try it out** → 요청 값 입력 → **Execute** 로 호출하고, 응답을 바로 확인할 수 있다.

### 2) 브라우저 주소창에서 바로 보기 (GET만)

| 확인하고 싶은 기능 | 주소 |
|--------------------|------|
| Kakao OAuth 인증 URL | http://localhost:8000/ |
| 서버 상태 | http://localhost:8000/health |
| 참여율 (Mock 기준) | http://localhost:8000/aggregation/participation-rate |
| 4주 지속률 (Mock 기준) | http://localhost:8000/aggregation/retention-4weeks |

### 3) POST API (접속 기록, 퀴즈 시작/완료, MVP 시퀀스)

POST는 **/docs** 에서 실행하는 것이 편하다.

- **POST /engagement/access**: body에 `{"user_id": "user-1"}` 입력 후 Execute
- **POST /quiz/start**: body에 `{"user_id": "user-1", "quiz_id": "quiz-1"}` 입력 후 Execute
- **POST /mvp/sequence**: body에 `{"user_id": "user-1", "score": 85}` 등 입력 후 Execute → 접속→시작→완료가 한 번에 실행되고 결과가 나온다.

이후 **참여율**·**4주 지속률**을 다시 호출하면 반영된 Mock 데이터 기준으로 값이 바뀐 것을 확인할 수 있다.

---

## 카카오 로그인 시 "로딩 중"이 끝나지 않을 때

가능한 원인과 확인 방법입니다.

### 1) **로그인 버튼 클릭 직후부터 로딩** (카카오 페이지로 안 넘어감)

- **원인:** 프론트에서 `auth_url`을 받기 위해 백엔드를 호출하는데, 응답이 안 오거나 에러를 처리하지 않음.
- **확인:**
  - 브라우저 개발자 도구(F12) → Network에서 "카카오 로그인" 클릭 시 요청이 가는지, `GET /` 또는 `GET /kakao-authentication/request-oauth-link` 가 200으로 오는지 확인.
  - 주소창에 직접 `http://localhost:8000/` 입력 시 JSON이 바로 나오는지 확인 (`auth_url`, `client_id` 등).
- **조치:** `.env`에 `KAKAO_CLIENT_ID`, `KAKAO_REDIRECT_URI`가 있는지 확인. 없으면 400 에러가 나고, 프론트가 이걸 처리하지 않으면 로딩처럼 보일 수 있음. 프론트에서는 응답 받은 뒤 **즉시** `window.location.href = auth_url` 로 이동하도록 구현.

### 2) **카카오 로그인 화면에서 제출 후 로딩** (백엔드 콜백 이후)

- **원인:** 백엔드가 토큰 발급 후 `FRONTEND_BASE_URL/login/callback` 으로 302 리다이렉트하는데, **프론트 서버가 꺼져 있거나 주소가 다름**.
- **확인:**
  - `.env`의 `FRONTEND_BASE_URL`이 실제 프론트 주소와 같은지 (예: `http://localhost:3000`).
  - 프론트 앱이 해당 주소에서 실행 중인지 (예: `npm run dev` 로 3000 포트).
- **조치:** 프론트를 띄운 뒤 다시 로그인. 또는 백엔드만 테스트할 때는 `FRONTEND_BASE_URL`을 `http://localhost:8000`으로 두고, `/login/callback` 라우트를 백엔드에 두는 식으로도 확인 가능.

### 3) **백엔드가 카카오 API 호출에서 멈춤**

- **원인:** 카카오 토큰/유저 API가 느리거나 타임아웃 없이 대기.
- **조치:** 카카오 API 호출에 타임아웃(15초/10초)을 넣어 두었음. 그래도 로딩이 길면 네트워크·방화벽을 확인하고, 터미널에서 백엔드 로그에 에러가 찍히는지 확인.

### 4) **카카오 로그인 페이지 자체가 안 뜸**

- **확인:** `http://localhost:8000/` 응답의 `auth_url`을 복사해 주소창에 붙여 넣었을 때 카카오 로그인 화면이 뜨는지 확인.
- **조치:** 네트워크/방화벽, 광고 차단 확장 프로그램이 kauth.kakao.com을 막고 있지 않은지 확인.
