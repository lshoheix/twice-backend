"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  getAccountId,
  postEngagementVisit,
  getKakaoOAuthLink,
  setAccountId,
} from "@/lib/api";

export default function HomePage() {
  const [accountId, setAccountIdState] = useState<string | null>(null);
  const [visitDone, setVisitDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAccountIdState(getAccountId());
  }, []);

  useEffect(() => {
    if (!accountId || visitDone) return;
    postEngagementVisit(accountId)
      .then(() => setVisitDone(true))
      .catch((e) => setError(e instanceof Error ? e.message : "Visit failed"));
  }, [accountId, visitDone]);

  const handleKakaoLogin = useCallback(() => {
    getKakaoOAuthLink()
      .then(({ auth_url }) => {
        window.location.href = auth_url;
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to get login link"));
  }, []);

  if (error) {
    return (
      <div>
        <p style={{ color: "crimson" }}>{error}</p>
      </div>
    );
  }

  if (!accountId) {
    return (
      <div>
        <h1>Learning MVP</h1>
        <p>Log in to continue.</p>
        <button
          type="button"
          onClick={handleKakaoLogin}
          style={{
            padding: "0.5rem 1rem",
            background: "#FEE500",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Login with Kakao
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>Learning MVP</h1>
      <p>Account: {accountId.slice(0, 8)}...</p>
      <nav style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
        <Link
          href="/quiz"
          style={{
            padding: "0.5rem 1rem",
            background: "#333",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
          }}
        >
          Start Quiz
        </Link>
        <Link
          href="/analytics"
          style={{
            padding: "0.5rem 1rem",
            background: "#666",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
          }}
        >
          View Analytics
        </Link>
      </nav>
    </div>
  );
}
