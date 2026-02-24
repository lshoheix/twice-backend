"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  getAccountId,
  postQuizStart,
  postQuizComplete,
  postQuizAbandon,
} from "@/lib/api";

export default function QuizPage() {
  const router = useRouter();
  const [accountId, setAccountIdState] = useState<string | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAccountIdState(getAccountId());
  }, []);

  const startQuiz = useCallback(() => {
    if (!accountId) return;
    setError(null);
    setResult(null);
    postQuizStart(accountId, "quiz-1", "MID")
      .then((r) => setAttemptId(r.attempt_id))
      .catch((e) => setError(e instanceof Error ? e.message : "Start failed"));
  }, [accountId]);

  const finishQuiz = useCallback(() => {
    if (!accountId || !attemptId) return;
    setError(null);
    const score = Math.floor(50 + Math.random() * 51);
    postQuizComplete(accountId, attemptId, score)
      .then(() => setResult(`Completed with score ${score}`))
      .catch((e) => setError(e instanceof Error ? e.message : "Finish failed"));
  }, [accountId, attemptId]);

  const exitQuiz = useCallback(() => {
    if (!accountId || !attemptId) return;
    setError(null);
    postQuizAbandon(accountId, attemptId)
      .then(() => router.push("/"))
      .catch((e) => setError(e instanceof Error ? e.message : "Exit failed"));
  }, [accountId, attemptId, router]);

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
      <h1>Quiz</h1>
      <Link href="/" style={{ marginBottom: "1rem", display: "inline-block" }}>
        Back to home
      </Link>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {result && <p style={{ color: "green" }}>{result}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <button
          type="button"
          onClick={startQuiz}
          style={{
            padding: "0.5rem 1rem",
            background: "#333",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Start Quiz
        </button>
        {attemptId && (
          <>
            <p>Attempt ID: {attemptId}</p>
            <button
              type="button"
              onClick={finishQuiz}
              style={{
                padding: "0.5rem 1rem",
                background: "green",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Finish (random 50–100)
            </button>
            <button
              type="button"
              onClick={exitQuiz}
              style={{
                padding: "0.5rem 1rem",
                background: "crimson",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Exit
            </button>
          </>
        )}
      </div>
    </div>
  );
}
