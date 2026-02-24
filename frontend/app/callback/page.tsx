"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { getKakaoTokenAndUser, setAccountId } from "@/lib/api";

function CallbackContent() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setStatus("error");
      setMessage("No code in URL");
      return;
    }
    getKakaoTokenAndUser(code)
      .then((data) => {
        if (data.account_id) {
          setAccountId(data.account_id);
          setStatus("ok");
          window.location.href = "/";
        } else {
          setStatus("error");
          setMessage("Backend did not return account_id");
        }
      })
      .catch((e) => {
        setStatus("error");
        setMessage(e instanceof Error ? e.message : "Login failed");
      });
  }, [searchParams]);

  if (status === "loading") return <p>Logging in...</p>;
  if (status === "error") {
    return (
      <div>
        <p style={{ color: "crimson" }}>{message}</p>
        <Link href="/">Back to home</Link>
      </div>
    );
  }
  return (
    <div>
      <p>Login successful.</p>
      <Link href="/">Go to home</Link>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <CallbackContent />
    </Suspense>
  );
}
