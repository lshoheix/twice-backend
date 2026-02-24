# 테스트를 위해 해야 할 사항

원하는 기능(카카오 로그인, 대시보드 집계, 퀴즈)을 실행·테스트하기 위한 체크리스트입니다.

---

## 1. 환경 준비

### 1-1. 프론트엔드 실행

```bash
cd /Users/lshoheix/Documents/GitHub/twice-frontend
npm install
npm run dev
```

- 브라우저에서 **http://localhost:3000** (또는 프론트가 쓰는 포트, 예: 3001) 접속 가능해야 함.

### 1-2. 환경 변수 (.env)

**프론트** 프로젝트 루트에 `.env` 파일을 만들고, 백엔드 주소를 넣습니다.

```env
# 백엔드 API 주소 (명세 기준 예: 8000)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

- `.env` 수정 후에는 `npm run dev`를 한 번 다시 실행하는 것이 좋습니다.

**백엔드** `.env`에는 다음이 필요합니다.

```env
KAKAO_CLIENT_ID=...
KAKAO_REDIRECT_URI=http://localhost:8000/kakao-authentication/request-access-token-after-redirection
FRONTEND_BASE_URL=http://localhost:3000
```

- `FRONTEND_BASE_URL`은 실제 프론트 주소로 (예: 3001 포트면 `http://localhost:3001`).

### 1-3. 백엔드 실행

- 백엔드 서버를 **http://localhost:8000** 에서 띄웁니다.
- CORS가 켜져 있어야 합니다 (프론트 localhost:3000/3001에서 API 호출 가능해야 함).

---

## 2. 카카오 로그인 테스트

### 백엔드에서 필요한 것

1. **카카오 로그인 후 JSON 응답 대신 프론트로 리다이렉트**
   - 리다이렉트 URL: `{FRONTEND_BASE_URL}/login/callback?access_token=...&refresh_token=...&user_id=...`
   - 예: `http://localhost:3000/login/callback?access_token=...` (또는 3001 등)
   - 백엔드에 “리다이렉트” 수정이 적용되어 있어야 함.

2. **카카오 앱 설정 (개발자 콘솔)**
   - **Redirect URI**에 **백엔드 콜백 URL**을 **그대로** 등록해야 함.
   - 예: `http://localhost:8000/kakao-authentication/request-access-token-after-redirection`
   - (`http://localhost:8000/callback` 아님 — 위 경로 전체가 맞음.)

### 내가 할 일

1. 브라우저에서 **http://localhost:3000/login** (또는 사용 중인 프론트 주소) 접속.
2. **카카오로 로그인** 버튼 클릭.
3. 카카오 로그인 화면에서 로그인.
4. 로그인 성공 시 **대시보드**(예: http://localhost:3000/dashboard)로 자동 이동하는지 확인.

- JSON만 보이고 리다이렉트가 안 되면 → 백엔드가 아직 리다이렉트를 안 하고 있는 것이므로, 백엔드 수정이 필요합니다.

### "콜백 페이지에서 계속 로딩만 돼요"

프론트가 `GET .../request-access-token-after-redirection?code=xxx` 호출 시 **`Accept: application/json`** 헤더를 보내면, 백엔드는 **302가 아니라 200 + JSON**으로 응답합니다.

- **응답 본문:** `{ "access_token": "...", "refresh_token": "...", "user": { "id", "nickname", "email", "profile_image_url" } }`
- 그러면 프론트가 토큰을 저장하고 바로 대시보드로 넘깁니다.
- 302만 주는 경우(브라우저가 카카오에서 그 URL로 직접 리다이렉트)에는 브라우저가 302를 따라가서 `/login/callback?access_token=...` 로 이동하므로, **콜백 페이지에서 쿼리를 읽고 저장 후 즉시 `/dashboard`로 이동**해야 로딩만 도는 일이 없습니다.

### 프론트 /login/callback 체크리스트 (구현 기준)

- 콜백이 열리자마자 `window.location.search`(또는 라우터 query)에서 **access_token, refresh_token, user_id** 를 반드시 읽기.
- **error** 쿼리가 있으면: 에러 메시지만 표시하고, 로딩 스피너는 돌리지 않기.
- **토큰**이 있으면: 저장(localStorage 등)한 뒤 바로 `/dashboard`로 이동. “로딩 끝날 때까지 기다렸다가 이동” 같은 추가 대기는 하지 않기.
- **팝업**으로 열린 경우(`window.opener` 존재): 위와 같이 읽고 저장한 다음 `postMessage`로 부모 창에 전달 → `window.close()`. 부모 창은 메시지 받으면 토큰 저장 후 `/dashboard`로 이동.

---

## 3. 대시보드(접속 기록 + 참여율/지속률) 테스트

### 내가 할 일

1. **로그인된 상태**에서 **http://localhost:3000/dashboard** 접속.
2. 확인할 것:
   - **참여율** 카드에 숫자(%, 접속/퀴즈 완료 인원)가 나오는지.
   - **4주 지속률** 카드에 숫자가 나오는지.
3. 로그인한 사용자라면 페이지 진입 시 **접속 기록 API**(`POST /engagement/access`)가 자동 호출됩니다. 백엔드 로그나 DB로 접속 기록이 쌓이는지 확인하면 됩니다.

- “집계 로딩 중…”만 나오거나 에러가 나면 → 백엔드가 떠 있는지, `.env`의 `NEXT_PUBLIC_API_BASE_URL`이 `http://localhost:8000`인지 확인.

---

## 4. 퀴즈(시작 → 제출) 테스트

### 내가 할 일

1. **로그인된 상태**에서 **http://localhost:3000/quiz** 접속.
2. **퀴즈 시작** 버튼 클릭 → “점수 (0~100)” 입력란과 **제출** 버튼이 보이는지 확인.
3. 점수 입력 후 **제출** 클릭.
4. “제출 완료”, 점수, 완료 시각이 나오는지 확인.

- 로그인 안 하면 “로그인해 주세요” 메시지가 나와야 합니다.

---

## 5. 한 번에 점검하는 순서 (요약)

| 순서 | 할 일 | 확인 |
|------|--------|------|
| 1 | `.env`에 `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` 설정 | — |
| 2 | 백엔드 서버 실행 (localhost:8000) | 브라우저에서 `http://localhost:8000/health` 등으로 확인 |
| 3 | `npm run dev`로 프론트 실행 | http://localhost:3000 (또는 3001) 접속 |
| 4 | http://localhost:3000/login → 카카오 로그인 | 대시보드로 리다이렉트되는지 |
| 5 | http://localhost:3000/dashboard | 참여율·4주 지속률 숫자 표시 |
| 6 | http://localhost:3000/quiz → 퀴즈 시작 → 점수 입력 → 제출 | 제출 완료·점수 표시 |

---

## 6. 백엔드가 프론트에게 받는 정보 (프론트 → 백엔드)

| API | 받는 것 |
|-----|--------|
| **카카오 콜백** | 쿼리: `code`. 헤더(선택): `Accept: application/json` 이면 200 JSON, 없으면 302. |
| **POST /engagement/access** | Body: `user_id` |
| **POST /quiz/start** | Body: `user_id`, `quiz_id` |
| **POST /quiz/finish** | Body: `session_id`, `score`, (선택) `improvement_rate`, `evaluation` |
| **GET** (OAuth URL, 참여율, 지속률, health) | 요청 본문/쿼리 없음 |

---

## 7. 자주 나오는 문제

- **카카오 로그인 후 JSON만 보임**  
  → 백엔드가 토큰 발급 후 프론트(`/login/callback?access_token=...`)로 리다이렉트하도록 수정해야 함.

- **대시보드/퀴즈에서 “로그인해 주세요” 또는 데이터가 안 나옴**  
  → 카카오 로그인이 완료된 뒤인지 확인. (콜백에서 토큰·user_id 저장되어야 함.)

- **API 에러 (네트워크/ CORS)**  
  → 백엔드 주소(localhost:8000), CORS 설정, `.env`의 `NEXT_PUBLIC_API_BASE_URL` 확인.

- **`next: command not found`**  
  → `rm -rf node_modules package-lock.json` 후 `npm install` 다시 실행.

- **카카오 Redirect URI 오류 (KOE101 등)**  
  → 개발자 콘솔에 등록한 Redirect URI가 `http://localhost:8000/kakao-authentication/request-access-token-after-redirection` 와 **완전히 일치**하는지 확인.
