"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import { btnPrimary } from "@/components/ui";

function VerifyContent() {
  const token = useSearchParams().get("token");
  const [status, setStatus] = useState(token ? "loading" : "error");
  const [message, setMessage] = useState(
    token ? "" : "This link is missing its token.",
  );

  useEffect(() => {
    if (!token) return;

    async function verify() {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify-email`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
          },
        );
        const data = await res.json();

        if (res.ok) {
          setStatus("success");
        } else {
          setStatus("error");
          setMessage(
            typeof data.detail === "string"
              ? data.detail
              : "Verification failed",
          );
        }
      } catch (err) {
        setStatus("error");
        setMessage("Cannot reach the server");
      }
    }

    verify();
  }, [token]);

  if (status === "loading") {
    return (
      <AuthLayout
        variant="register"
        title="Verifying your email..."
        subtitle="This only takes a moment."
      >
        <p className="font-code text-sm text-cyan-400">
          $ verifying<span className="anim-blink">▍</span>
        </p>
      </AuthLayout>
    );
  }

  if (status === "success") {
    return (
      <AuthLayout
        variant="register"
        title="Email verified 🎉"
        subtitle="Your account is ready. You can log in now."
      >
        <Link href="/login" className={`${btnPrimary} block w-full`}>
          Go to login
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      variant="register"
      title="Verification failed"
      subtitle="We could not verify your email."
    >
      <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
        {message}
      </p>
      <Link href="/register" className={`${btnPrimary} mt-6 block w-full`}>
        Back to register
      </Link>
    </AuthLayout>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyContent />
    </Suspense>
  );
}
