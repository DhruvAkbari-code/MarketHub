"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import { btnPrimary } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/forgot-password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        },
      );
      const data = await res.json();
      if (!res.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Something went wrong",
        );
      } else {
        setSent(true);
      }
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      variant="forgot"
      title="Reset password"
      subtitle="We'll email you a reset link."
    >
      {sent ? (
        <p className="rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
          A reset link has been sent to {email}. Check your inbox.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={inputClass}
          />
          {error && (
            <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className={`${btnPrimary} w-full`}
          >
            {loading ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}
      <p className="mt-6 text-center text-sm text-slate-500">
        <Link
          href="/login"
          className="font-semibold text-cyan-400 hover:underline"
        >
          Back to login
        </Link>
      </p>
    </AuthLayout>
  );
}
