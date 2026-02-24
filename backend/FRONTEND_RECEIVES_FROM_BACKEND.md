# 프론트엔드가 백엔드에게 받는 정보

백엔드 API 호출 시 **프론트가 응답으로 받는 데이터** 정리입니다.  
Base URL 예: `http://localhost:8000` (환경에 따라 변경)

---

## 1. 카카오 OAuth

### 1-1. 로그인 URL 발급

- **요청:** `GET {baseUrl}/` 또는 `GET {baseUrl}/kakao-authentication/request-oauth-link`
- **응답 (JSON):**
  - `auth_url` (string) — 이 URL로 이동하면 카카오 로그인 화면
  - `client_id` (string)
  - `redirect_uri` (string)
  - `response_type` (string, 보통 `"code"`)

### 1-2. 로그인 콜백 – JSON으로 받는 경우

- **요청:** `GET {baseUrl}/kakao-authentication/request-access-token-after-redirection?code={인가코드}`  
  **헤더:** `Accept: application/json`
- **응답 (200 JSON):**
  - `access_token` (string)
  - `token_type` (string, 보통 `"bearer"`)
  - `refresh_token` (string, 있을 수 있음)
  - `expires_in` (number, 있을 수 있음)
  - `refresh_token_expires_in` (number, 있을 수 있음)
  - `user` (object, 있을 수 있음)
    - `id` (number) — **이 값을 `user_id`로 사용** (engagement/quiz API 호출 시)
    - `nickname` (string, 있을 수 있음)
    - `email` (string, 있을 수 있음)
    - `profile_image_url` (string, 있을 수 있음)

### 1-3. 로그인 콜백 – 302 리다이렉트로 받는 경우

- 브라우저가 카카오에서 백엔드로 리다이렉트된 뒤, 백엔드가 **302**로 프론트 `/login/callback`으로 보냄.
- **프론트가 받는 것:** **URL 쿼리 파라미터** (예: `http://localhost:3001/login/callback?access_token=...&refresh_token=...&user_id=...`)
  - `access_token` (string)
  - `refresh_token` (string, 있을 수 있음)
  - `user_id` (string, 있을 수 있음 — 카카오 사용자 id)
  - 에러 시: `error` (string, URL 인코딩된 메시지)
- **할 일:** `/login/callback` 페이지에서 위 쿼리를 읽어 저장한 뒤 **즉시** `/dashboard`로 이동.

---

## 2. 서비스 접속 기록

- **요청:** `POST {baseUrl}/engagement/access`  
  **Body (JSON):** `{ "user_id": "..." }`
- **응답 (JSON):**
  - `user_id` (string)
  - `accessed_at` (string, ISO 8601 날짜·시간)
  - `access_id` (string)

---

## 3. 퀴즈

### 3-1. 퀴즈 시작

- **요청:** `POST {baseUrl}/quiz/start`  
  **Body (JSON):** `{ "user_id": "...", "quiz_id": "..." }`
- **응답 (JSON):**
  - `session_id` (string) — **퀴즈 완료 시 이 값을 넘겨야 함**
  - `user_id` (string)
  - `quiz_id` (string)
  - `state` (string, `"start"`)
  - `started_at` (string, ISO 8601)

### 3-2. 퀴즈 완료

- **요청:** `POST {baseUrl}/quiz/finish`  
  **Body (JSON):** `{ "session_id": "...", "score": 85, "improvement_rate": 10, "evaluation": "Good" }` (improvement_rate, evaluation은 선택)
- **응답 (JSON):**
  - `session_id`, `user_id`, `quiz_id`, `state` (`"finish"`), `started_at`, `finished_at` (string, ISO 8601), `score`, `improvement_rate`, `evaluation`

---

## 4. 집계 (대시보드)

### 4-1. 참여율

- **요청:** `GET {baseUrl}/aggregation/participation-rate`
- **응답 (JSON):**
  - `participation_rate` (number, %)
  - `total_accessed` (number)
  - `total_finished_quiz` (number)

### 4-2. 4주 지속률

- **요청:** `GET {baseUrl}/aggregation/retention-4weeks`
- **응답 (JSON):**
  - `retention_4weeks` (number, %)
  - `baseline_count` (number)
  - `retained_count` (number)

---

## 5. 기타

- **요청:** `GET {baseUrl}/health`
- **응답 (JSON):** `{ "status": "ok" }`

---

## 요약 표

| API | 프론트가 받는 것 |
|-----|------------------|
| GET `/` 또는 `/request-oauth-link` | JSON: `auth_url`, `client_id`, `redirect_uri`, `response_type` |
| 콜백 (Accept: application/json) | JSON: `access_token`, `refresh_token`, `user` (id, nickname, email, profile_image_url). `user.id` → `user_id`로 사용. |
| 콜백 (302 리다이렉트) | URL 쿼리: `access_token`, `refresh_token`, `user_id` (또는 `error`) |
| POST `/engagement/access` | JSON: `user_id`, `accessed_at`, `access_id` |
| POST `/quiz/start` | JSON: `session_id`, `user_id`, `quiz_id`, `state`, `started_at` → **session_id를 퀴즈 완료 시 넘겨야 함** |
| POST `/quiz/finish` | JSON: `session_id`, `user_id`, `quiz_id`, `state`, `score`, `finished_at` 등 |
| GET `/aggregation/participation-rate` | JSON: `participation_rate`, `total_accessed`, `total_finished_quiz` |
| GET `/aggregation/retention-4weeks` | JSON: `retention_4weeks`, `baseline_count`, `retained_count` |
| GET `/health` | JSON: `{ "status": "ok" }` |

---

이 문서를 프론트엔드 팀에 전달해 사용하시면 됩니다.
