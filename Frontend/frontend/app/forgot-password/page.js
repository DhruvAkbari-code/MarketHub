"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import { btnPrimary } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    // The reset-password API will be connected in a later step
    setSent(true);
  }

  return (
    <AuthLayout
      variant="forgot"
      title="Reset password"
      subtitle="We'll email you a reset link."
    >
      {sent ? (
        <p className="rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
          If an account exists for {email}, a reset link is on its way.
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
          <button type="submit" className={`${btnPrimary} w-full`}>
            Send reset link
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
