# 프론트엔드 연동용 API 명세

백엔드(base URL)는 환경에 따라 설정 (예: `http://localhost:8000`).  
일반 API 응답은 JSON이며, 날짜/시간은 ISO 8601 형식 문자열입니다.  
**카카오 OAuth 콜백**은 JSON이 아니라 **302 리다이렉트**로 동작합니다.

---

## 1. Kakao 인증

### 1-1. OAuth 인증 URL 발급 (로그인 버튼용)

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `{baseUrl}/` 또는 `{baseUrl}/kakao-authentication/request-oauth-link` |
| **요청** | 없음 |
| **응답** | 아래 JSON |

**응답 예시**
```json
{
  "auth_url": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code",
  "client_id": "84ade12f93f42d3c9337e5de085ea556",
  "redirect_uri": "http://localhost:8000/kakao-authentication/request-access-token-after-redirection",
  "response_type": "code"
}
```

**프론트 사용:** `auth_url`로 이동시키면 Kakao 로그인 페이지로 이동.  
카카오 쪽 Redirect URI는 반드시 **백엔드 콜백 URL**이어야 하며, 예: `http://localhost:8000/kakao-authentication/request-access-token-after-redirection`.

---

### 1-2. 카카오 OAuth 콜백 (200 JSON 또는 302 리다이렉트)

사용자가 카카오 로그인을 마치면, 카카오가 **백엔드** 아래 URL로 리다이렉트합니다.  
백엔드는 **Accept 헤더**에 따라 다르게 응답합니다.

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `{baseUrl}/kakao-authentication/request-access-token-after-redirection?code={인가코드}` |

**동작 분기**

- **`Accept: application/json`** 이 포함된 요청 (프론트에서 fetch/axios로 호출 시):  
  **200 + JSON** 으로 `access_token`, `refresh_token`, `user` 를 그대로 반환.  
  → 프론트가 토큰을 저장하고 바로 대시보드로 이동할 수 있어, 콜백 페이지에서 로딩만 도는 문제를 피할 수 있음.
- **그 외** (브라우저가 카카오에서 그대로 이 URL로 리다이렉트한 경우):  
  **302 리다이렉트** → `{FRONTEND_BASE_URL}/login/callback?access_token=...&refresh_token=...&user_id=...`

**200 JSON 응답 (Accept: application/json 인 경우)**

응답 본문 예시:
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "refresh_token": "...",
  "expires_in": 21599,
  "refresh_token_expires_in": 5183999,
  "user": {
    "id": 12345678,
    "nickname": "홍길동",
    "email": "user@example.com",
    "profile_image_url": "https://..."
  }
}
```
프론트에서 이 URL을 **fetch/axios**로 호출할 때 **`Accept: application/json`** 헤더를 넣으면 위 JSON만 받고, 302를 따라가지 않으므로 토큰 저장 후 대시보드로 이동하기 좋습니다.

**302 리다이렉트 시 쿼리 파라미터 (Accept가 application/json이 아닐 때, 성공 시)**

| 파라미터 | 설명 |
|----------|------|
| `access_token` | 카카오 액세스 토큰 (항상 포함) |
| `refresh_token` | 카카오 리프레시 토큰 (있을 때만) |
| `user_id` | 우리 서비스에서 쓸 사용자 ID (카카오 사용자 id, engagement/quiz API 호출 시 사용) |

**예시 (302 성공)**  
`http://localhost:3000/login/callback?access_token=xxx&refresh_token=yyy&user_id=12345678`

**에러 시**  
같은 경로에 `error` 쿼리 파라미터로 메시지 전달:  
`http://localhost:3000/login/callback?error=토큰%20발급%20실패...`

**302의 Location 헤더 확인 (백엔드 검증)**  
백엔드는 반드시 **302**와 함께 **Location** 헤더를 아래 형식으로 내려줍니다.

- 형식: `{FRONTEND_BASE_URL}/login/callback?access_token=...&refresh_token=...&user_id=...`
- 확인 방법 (인가 코드 `code` 필요):
  ```bash
  curl -I "http://localhost:8000/kakao-authentication/request-access-token-after-redirection?code=유효한인가코드"
  ```
  응답에 `HTTP/1.1 302 Found`와 `Location: http://localhost:3000/login/callback?access_token=...` 이 포함되면 정상입니다. (브라우저 개발자 도구 → Network에서 해당 요청 선택 후 Response Headers의 Location으로도 확인 가능)

**권장 로그인 흐름 (프론트)**

1. 프론트가 `request-access-token-after-redirection?code=xxx` 호출 (카카오 리다이렉트로 이 URL에 도달한 경우 그대로 사용).
2. 백엔드가 **302** + **Location: `http://localhost:3000/login/callback?access_token=...&refresh_token=...&user_id=...`** 응답.
3. 프론트는 리다이렉트를 자동으로 따라가지 않고, **받은 Location URL로 `window.location.href = locationUrl`** 로 이동.
4. 같은 페이지가 **`/login/callback?access_token=...&refresh_token=...&user_id=...`** 로 다시 로드됨.
5. URL 쿼리에서 토큰/`user_id`를 읽어 저장한 뒤 **대시보드로 이동**.

이 흐름으로 로딩이 끝나고 대시보드까지 진행할 수 있습니다. 카카오 로그인 한 번 더 테스트해 보시면 됩니다.

**프론트엔드에서 할 일**

1. **`/login/callback`** 페이지(또는 라우트)를 만든다.
2. 페이지 로드 시 `window.location.search` 또는 라우터의 query에서 `access_token`, `refresh_token`, `user_id`를 꺼낸다.
3. `error`가 있으면 에러 메시지 표시, 없으면 토큰/`user_id`를 저장(예: localStorage, state)하고 메인 화면으로 이동.
4. 이후 engagement/quiz API 호출 시 `user_id`를 사용한다.

**QR 로그인 시 "다음이 안 넘어가요" (팝업 처리)**

카카오 **QR 로그인**은 로그인 완료 후 리다이렉트가 **팝업 창**에서 일어날 수 있습니다.  
그러면 `/login/callback`이 **팝업**에만 열리고, 메인 창(QR 보여주던 페이지)은 그대로 대기 상태로 남아 "다음이 안 넘어가는" 것처럼 보입니다.

- **프론트 대응 (권장):**
  1. **`/login/callback`** 페이지에서 `window.opener`가 있는지 확인 (팝업으로 열렸는지).
  2. **팝업인 경우:**  
     - URL에서 `access_token`, `refresh_token`, `user_id`(또는 `error`)를 읽고  
     - `window.opener.postMessage({ type: 'kakao-login', access_token, refresh_token, user_id })` 로 **메인 창에 전달**  
     - `window.close()` 로 팝업만 닫기.
  3. **메인 창(로그인 시작한 페이지)**에서는 `window.addEventListener('message', ...)` 로 위 메시지를 받으면 토큰을 저장하고 대시보드로 이동.

- **또는:** 로그인 시작 시 **같은 창**에서만 진행되도록 카카오 로그인 URL을 열면 (새 창/팝업 없이), QR이 아닌 일반 로그인처럼 같은 창에서 콜백이 열려 "다음이 안 넘어가는" 문제는 없을 수 있습니다. (카카오 SDK/정책에 따라 동작이 다를 수 있음.)

**"카카오에서는 로그인됐는데 서비스만 무한 대기"일 때**

카카오에서 "로그인되었습니다"까지 나왔는데 우리 서비스 화면은 계속 로딩만 도는 경우, **콜백 페이지(`/login/callback`)가 URL을 처리하지 않거나 대시보드로 넘기지 않아서**인 경우가 많습니다.

- **원인 요약**
  - 백엔드는 302로 `.../login/callback?access_token=...&user_id=...` 를 잘 보냄.
  - 브라우저는 그 주소로 이동해 **콜백 페이지를 연다**.
  - 그런데 콜백 페이지가 **쿼리(access_token, user_id)를 읽지 않거나**, 읽었는데 **저장/리다이렉트를 하지 않고** 로딩 UI만 보여 주면 → 사용자 입장에선 "무한 대기".

- **프론트에서 반드시 할 일**
  1. **페이지가 로드되자마자** `window.location.search`(또는 라우터 query)에서 `access_token`, `refresh_token`, `user_id`를 읽기.
  2. **`error`가 있으면** 에러 메시지만 표시 (로딩 유지 X).
  3. **토큰이 있으면** 저장(예: localStorage, 전역 상태)한 뒤 **즉시** `/dashboard`(또는 메인)로 이동 (`window.location.href = '/dashboard'` 또는 라우터 push). **로딩 스피너 뒤에 다른 화면을 기다리지 말 것.**
  4. **팝업인 경우** (`window.opener` 있음): 위처럼 읽고 저장한 다음 `postMessage`로 부모에 전달 후 `window.close()`, 부모는 메시지 받으면 저장하고 `/dashboard`로 이동.

- **점검**
  - 카카오 로그인 직후 주소창이 `http://localhost:3000/login/callback?access_token=...` 인지 확인.
  - 그 상태에서 새로고침(F5)했을 때 콜백 페이지가 토큰을 읽고 대시보드로 보내는지 확인.
  - 콜백 페이지 코드에서 "쿼리 읽기 → 저장 → redirect"가 **한 번의 로드 안에서** 빠짐없이 실행되는지 확인 (useEffect/onMount 등에서 한 번만 실행되도록).

**무한 대기 – 다른 원인 점검 (백엔드/환경)**

콜백 페이지를 수정해도 계속 무한 대기라면 아래를 순서대로 확인하세요.

| 확인 | 방법 |
|------|------|
| **1. 카카오 로그인 직후 주소창** | "로그인되었습니다" 직후 **지금 보이는 창의 주소창**에 뭐가 있는지 봅니다. `https://kauth.kakao.com/...` 인지, `http://localhost:8000/...` 인지, `http://localhost:3000/login/callback?access_token=...` 인지. |
| **2. 백엔드 로그** | 카카오 로그인 버튼 클릭 → 카카오에서 로그인 완료한 **직후** 백엔드 터미널에 로그가 찍히는지 봅니다. `kakao_callback request ...`, `kakao_callback redirect (success) -> http://localhost:3000/login/callback?...` 같은 로그가 있으면 백엔드까지는 정상. **로그가 전혀 없으면** 카카오가 우리 백엔드로 리다이렉트를 안 하고 있는 것(Redirect URI 불일치 등)일 수 있음. |
| **3. 리다이렉트 URL 확인** | 위 로그에 찍힌 `redirect (success) ->` 뒤의 URL을 복사해 브라우저 주소창에 붙여 넣어 봅니다. 그 주소가 **실제로 열리는지**, 프론트가 그 포트에서 떠 있는지 확인. (예: `http://localhost:3000/login/callback?access_token=...` 이면 3000번 포트 프론트가 떠 있어야 함.) |
| **4. .env의 FRONTEND_BASE_URL** | 백엔드 `.env`에 `FRONTEND_BASE_URL=http://localhost:3000` (또는 실제 프론트 주소)가 맞는지, 오타·다른 포트·trailing slash 없는지 확인. |
| **5. Next.js에서 쿼리 읽기** | Next.js App Router에서는 `searchParams`가 클라이언트에서 첫 렌더 후에 올 수 있어서, 첫 화면에선 빈 값일 수 있음. 콜백 페이지에서 **`window.location.search`** 를 직접 읽어서 처리하거나, `useSearchParams()` + `useEffect`에서 한 번 읽은 뒤 저장·리다이렉트하도록 하세요. |

- **정리:** 백엔드 로그에 `kakao_callback redirect (success) -> ...` 가 찍히는데도 브라우저가 그 URL로 안 넘어가면 → 리다이렉트 대상 주소/프론트 서버 확인. 로그가 아예 없으면 → 카카오 Redirect URI와 백엔드 콜백 URL이 일치하는지 확인.

---

## 2. Engagement (서비스 접속)

### 2-1. 서비스 접속 기록

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `{baseUrl}/engagement/access` |
| **요청 Body** | `{ "user_id": "수강생ID" }` |
| **응답** | 아래 JSON |

**응답 예시**
```json
{
  "user_id": "user-1",
  "accessed_at": "2025-02-24T10:00:00.000Z",
  "access_id": "acc-a1b2c3d4"
}
```

**프론트 사용:** 앱/페이지 진입 시 한 번 호출해 접속 이력 기록.

---

## 3. Quiz (퀴즈)

### 3-1. 퀴즈 시작

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `{baseUrl}/quiz/start` |
| **요청 Body** | `{ "user_id": "수강생ID", "quiz_id": "퀴즈ID" }` |
| **응답** | 아래 JSON |

**응답 예시**
```json
{
  "session_id": "sess-x7y8z9",
  "user_id": "user-1",
  "quiz_id": "quiz-1",
  "state": "start",
  "started_at": "2025-02-24T10:05:00.000Z"
}
```

**프론트 사용:** 퀴즈 시작 시 호출. 응답의 `session_id`를 **완료 API**에 그대로 넘겨야 함.

---

### 3-2. 퀴즈 완료 (점수 저장)

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `{baseUrl}/quiz/finish` |
| **요청 Body** | 아래 JSON |
| **응답** | 아래 JSON |

**요청 Body 예시**
```json
{
  "session_id": "sess-x7y8z9",
  "score": 85.0,
  "improvement_rate": 10.5,
  "evaluation": "Good"
}
```
- `session_id`: (필수) 퀴즈 시작 시 받은 값
- `score`: (필수) 0~100
- `improvement_rate`, `evaluation`: (선택)

**응답 예시**
```json
{
  "session_id": "sess-x7y8z9",
  "user_id": "user-1",
  "quiz_id": "quiz-1",
  "state": "finish",
  "started_at": "2025-02-24T10:05:00.000Z",
  "finished_at": "2025-02-24T10:20:00.000Z",
  "score": 85.0,
  "improvement_rate": 10.5,
  "evaluation": "Good"
}
```

**프론트 사용:** 퀴즈 제출 시 위 body로 호출. 이후 대시보드 등에 결과 표시.

---

## 4. Aggregation (집계)

### 4-1. 참여율

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `{baseUrl}/aggregation/participation-rate` |
| **요청** | 없음 |
| **응답** | 아래 JSON |

**응답 예시**
```json
{
  "participation_rate": 66.67,
  "total_accessed": 3,
  "total_finished_quiz": 2
}
```

**프론트 사용:** 대시보드 참여율 숫자/차트에 사용.

---

### 4-2. 4주 지속률

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `{baseUrl}/aggregation/retention-4weeks` |
| **요청** | 없음 |
| **응답** | 아래 JSON |

**응답 예시**
```json
{
  "retention_4weeks": 50.0,
  "baseline_count": 10,
  "retained_count": 5
}
```

**프론트 사용:** 대시보드 지속률 표시.

---

## 5. MVP 시퀀스 (접속 → 시작 → 완료 한 번에)

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `{baseUrl}/mvp/sequence` |
| **요청 Body** | 아래 JSON |
| **응답** | 접속·시작·완료 3단계 결과를 한 번에 |

**요청 Body 예시**
```json
{
  "user_id": "user-1",
  "quiz_id": "quiz-1",
  "score": 80.0,
  "improvement_rate": 5.0,
  "evaluation": "Good"
}
```
- `user_id`: (필수)
- `quiz_id`: (선택, 기본 "quiz-1")
- `score`: (선택, 기본 80)
- `improvement_rate`, `evaluation`: (선택)

**응답 예시**
```json
{
  "step1_access": { "user_id": "user-1", "accessed_at": "...", "access_id": "acc-..." },
  "step2_start": { "session_id": "sess-...", "user_id": "user-1", "quiz_id": "quiz-1", "state": "start", "started_at": "..." },
  "step4_5_6_finish": { "session_id": "sess-...", "user_id": "user-1", "state": "finish", "score": 80.0, "finished_at": "...", ... }
}
```

**프론트 사용:** 데모/테스트용. 실제 서비스에서는 접속·시작·완료를 각각 호출하는 것을 권장.

---

## 6. 기타

| 용도 | Method | URL | 비고 |
|------|--------|-----|------|
| 서버 상태 | `GET` | `{baseUrl}/health` | `{ "status": "ok" }` |

---

## 백엔드 ↔ 프론트 주고받는 정보 요약

### 1. 백엔드가 프론트에게 **받는** 정보 (프론트 → 백엔드 요청 시)

| API | Method | 백엔드가 받는 것 |
|-----|--------|------------------|
| 카카오 콜백 | GET | **쿼리:** `code` (카카오 인가 코드, 카카오가 리다이렉트할 때 붙음). **헤더(선택):** `Accept: application/json` 이면 200 JSON, 없으면 302 리다이렉트. |
| 서비스 접속 기록 | POST `/engagement/access` | **Body (JSON):** `user_id` (문자열, 필수) |
| 퀴즈 시작 | POST `/quiz/start` | **Body (JSON):** `user_id` (필수), `quiz_id` (필수) |
| 퀴즈 완료 | POST `/quiz/finish` | **Body (JSON):** `session_id` (필수), `score` (필수, 0~100), `improvement_rate` (선택), `evaluation` (선택) |
| MVP 시퀀스 | POST `/mvp/sequence` | **Body (JSON):** `user_id` (필수), `quiz_id` (선택), `score` (선택), `improvement_rate` (선택), `evaluation` (선택) |
| OAuth URL 발급 / 참여율 / 4주 지속률 / health | GET | **없음** (요청 본문·쿼리 없음) |

---

### 2. 프론트가 백엔드에게 **받는** 정보 (백엔드 → 프론트 응답)

| API | 프론트가 받는 것 |
|-----|------------------|
| **GET /** 또는 **GET /kakao-authentication/request-oauth-link** | **JSON:** `auth_url`, `client_id`, `redirect_uri`, `response_type`. → `auth_url`로 이동하면 카카오 로그인. |
| **GET .../request-access-token-after-redirection** (Accept: application/json 인 경우) | **JSON:** `access_token`, `token_type`, `refresh_token`, `expires_in`, `refresh_token_expires_in`, `user` (객체: `id`, `nickname`, `email`, `profile_image_url`). `user.id`를 `user_id`로 쓰면 됨. |
| **GET .../request-access-token-after-redirection** (브라우저 리다이렉트, 302) | **리다이렉트 URL 쿼리:** `access_token`, `refresh_token`(있으면), `user_id`(있으면). 에러 시 `error`. → `/login/callback` 페이지에서 이 쿼리를 읽어 저장. |
| **POST /engagement/access** | **JSON:** `user_id`, `accessed_at`, `access_id` |
| **POST /quiz/start** | **JSON:** `session_id`, `user_id`, `quiz_id`, `state`, `started_at`. → `session_id`를 퀴즈 완료 시 넘겨야 함. |
| **POST /quiz/finish** | **JSON:** `session_id`, `user_id`, `quiz_id`, `state`, `started_at`, `finished_at`, `score`, `improvement_rate`, `evaluation` |
| **GET /aggregation/participation-rate** | **JSON:** `participation_rate` (%), `total_accessed`, `total_finished_quiz` |
| **GET /aggregation/retention-4weeks** | **JSON:** `retention_4weeks` (%), `baseline_count`, `retained_count` |
| **GET /health** | **JSON:** `{ "status": "ok" }` |

---

### 3. 무한 로딩 시 프론트 콜백 페이지가 꼭 할 일

- **입력(받는 것):** URL 쿼리 `access_token`, `refresh_token`, `user_id` (또는 `error`).
- **저장:** `access_token`, `refresh_token`, `user_id`를 localStorage/전역 상태 등에 저장. (`user_id`가 없으면 `access_token`만이라도 저장해 두고, 다른 API에서 필요 시 대체값 사용.)
- **다음 단계:** 저장 직후 **즉시** `/dashboard`(또는 메인)로 이동. **로딩만 보여 주고 끝나지 말 것.**  
- Next.js 등에서는 **`window.location.search`** 로 쿼리를 읽는 쪽이 안정적 (서버/클라이언트 모두에서 동일하게 동작).

---

## 프론트엔드에서 쓸 때 정리

1. **Base URL**  
   개발: `http://localhost:8000` (또는 실제 백엔드 주소)

2. **로그인 플로우**  
   - `GET /` 또는 `GET /kakao-authentication/request-oauth-link` → 응답의 `auth_url`로 사용자를 이동  
   - 카카오 로그인 후 카카오가 **백엔드** 콜백 URL로 리다이렉트 (code 포함)  
   - 백엔드가 토큰 발급 후 **프론트엔드** `{FRONTEND_BASE_URL}/login/callback?access_token=...&refresh_token=...&user_id=...` 로 **302 리다이렉트**  
   - 프론트는 `/login/callback` 페이지에서 쿼리 파라미터로 `access_token`, `refresh_token`, `user_id`를 받아 저장 후 메인 화면으로 이동. 에러 시 `error` 파라미터로 메시지 수신.

3. **수강생 액션**  
   - 진입: `POST /engagement/access` (body: `user_id`)  
   - 퀴즈 시작: `POST /quiz/start` → 받은 `session_id` 보관  
   - 퀴즈 제출: `POST /quiz/finish` (body에 `session_id`, `score` 등)

4. **대시보드**  
   - `GET /aggregation/participation-rate`  
   - `GET /aggregation/retention-4weeks`

5. **CORS**  
   백엔드에 CORS 미들웨어가 설정되어 있어, 다른 origin(예: 프론트 localhost:3000)에서도 위 API 호출 가능.
