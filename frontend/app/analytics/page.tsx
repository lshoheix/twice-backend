"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getAccountId,
  getAnalyticsParticipation,
  getAnalyticsRetention4w,
  getQuizHistory,
  type QuizAttemptItem,
} from "@/lib/api";

function formatDate(s: string | null): string {
  if (!s) return "-";
  try {
    const d = new Date(s);
    return d.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return s;
  }
}

export default function AnalyticsPage() {
  const [accountId, setAccountIdState] = useState<string | null>(null);
  const [participation, setParticipation] = useState<{
    target_users: number;
    finished_users: number;
    participation_rate: number;
  } | null>(null);
  const [retention, setRetention] = useState<{
    total_users: number;
    retained_users: number;
    retention_rate: number;
  } | null>(null);
  const [quizHistory, setQuizHistory] = useState<QuizAttemptItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAccountIdState(getAccountId());
  }, []);

  useEffect(() => {
    if (!accountId) return;
    const today = new Date();
    const to = today.toISOString().slice(0, 10);
    const fromDate = new Date(today);
    fromDate.setDate(fromDate.getDate() - 30);
    const from = fromDate.toISOString().slice(0, 10);
    const anchor = today.toISOString().slice(0, 10);

    getAnalyticsParticipation(from, to)
      .then(setParticipation)
      .catch((e) => setError(e instanceof Error ? e.message : "Participation failed"));
    getAnalyticsRetention4w(anchor)
      .then(setRetention)
      .catch((e) => setError(e instanceof Error ? e.message : "Retention failed"));
    getQuizHistory(accountId)
      .then(setQuizHistory)
      .catch((e) => setError(e instanceof Error ? e.message : "Quiz history failed"));
  }, [accountId]);

  if (!accountId) {
    return (
      <div>
        <p>Please log in first.</p>
        <Link href="/">Home</Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Analytics</h1>
      <Link href="/" style={{ marginBottom: "1rem", display: "inline-block" }}>
        Back to home
      </Link>
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <section style={{ marginTop: "1rem" }}>
        <h2>Participation (last 30 days)</h2>
        {participation ? (
          <ul style={{ listStyle: "none", padding: 0 }}>
            <li><strong>서비스 접속자 수:</strong> {participation.target_users}</li>
            <li>완료 사용자: {participation.finished_users}</li>
            <li>참여율: {(participation.participation_rate * 100).toFixed(2)}%</li>
          </ul>
        ) : (
          <p>Loading...</p>
        )}
      </section>

      <section style={{ marginTop: "1rem" }}>
        <h2>4-week retention</h2>
        {retention ? (
          <ul style={{ listStyle: "none", padding: 0 }}>
            <li><strong>서비스 접속자 수:</strong> {retention.total_users}</li>
            <li>지속 사용자: {retention.retained_users}</li>
            <li>4주 지속률: {(retention.retention_rate * 100).toFixed(2)}%</li>
          </ul>
        ) : (
          <p>Loading...</p>
        )}
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>내 퀴즈 이력</h2>
        {quizHistory ? (
          quizHistory.length === 0 ? (
            <p>퀴즈 이력이 없습니다.</p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {quizHistory.map((a) => (
                <li
                  key={a.id}
                  style={{
                    padding: "0.5rem 0",
                    borderBottom: "1px solid #eee",
                  }}
                >
                  {a.quiz_id} | 난이도 {a.difficulty_level} | 상태 {a.status}
                  {a.score != null && ` | 점수 ${a.score}`}
                  {" "}
                  | {formatDate(a.created_at)}
                  {a.finished_at && ` ~ ${formatDate(a.finished_at)}`}
                </li>
              ))}
            </ul>
          )
        ) : (
          <p>Loading...</p>
        )}
      </section>
    </div>
  );
}
