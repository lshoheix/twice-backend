const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getAccountId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("account_id");
}

export function setAccountId(accountId: string): void {
  if (typeof window !== "undefined") localStorage.setItem("account_id", accountId);
}

export async function getKakaoOAuthLink(): Promise<{
  auth_url: string;
  client_id: string;
  redirect_uri: string;
  response_type: string;
}> {
  const res = await fetch(`${BASE_URL}/kakao-authentication/request-oauth-link`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getKakaoTokenAndUser(code: string): Promise<{
  access_token: string;
  user?: { id: number };
  account_id?: string | null;
}> {
  const res = await fetch(
    `${BASE_URL}/kakao-authentication/request-access-token-after-redirection?code=${encodeURIComponent(code)}`
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function postEngagementVisit(accountId: string): Promise<{ ok: boolean }> {
  const res = await fetch(`${BASE_URL}/engagement/visit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account_id: accountId }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function postQuizStart(
  accountId: string,
  quizId: string,
  difficultyLevel: "LOW" | "MID" | "HIGH"
): Promise<{ attempt_id: string }> {
  const res = await fetch(`${BASE_URL}/quiz/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      account_id: accountId,
      quiz_id: quizId,
      difficulty_level: difficultyLevel,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function postQuizComplete(
  accountId: string,
  attemptId: string,
  score: number
): Promise<{ ok: boolean }> {
  const res = await fetch(`${BASE_URL}/quiz/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      account_id: accountId,
      attempt_id: attemptId,
      score,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function postQuizAbandon(
  accountId: string,
  attemptId: string
): Promise<{ ok: boolean }> {
  const res = await fetch(`${BASE_URL}/quiz/abandon`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account_id: accountId, attempt_id: attemptId }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAnalyticsParticipation(
  fromDate: string,
  toDate: string
): Promise<{ target_users: number; finished_users: number; participation_rate: number }> {
  const res = await fetch(
    `${BASE_URL}/analytics/participation?from=${fromDate}&to=${toDate}`
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAnalyticsRetention4w(
  anchorDate: string
): Promise<{ total_users: number; retained_users: number; retention_rate: number }> {
  const res = await fetch(
    `${BASE_URL}/analytics/retention/4w?anchor_date=${anchorDate}`
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export type QuizAttemptItem = {
  id: string;
  quiz_id: string;
  difficulty_level: string;
  status: string;
  score: number | null;
  created_at: string | null;
  finished_at: string | null;
};

export async function getQuizHistory(
  accountId: string
): Promise<QuizAttemptItem[]> {
  const res = await fetch(
    `${BASE_URL}/quiz/history?account_id=${encodeURIComponent(accountId)}`
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export { getAccountId };
