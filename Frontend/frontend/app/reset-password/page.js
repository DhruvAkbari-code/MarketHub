"use client";
import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import PasswordInput from "@/components/PasswordInput";
import { btnPrimary } from "@/components/ui";

function ResetContent() {
  const token = useSearchParams().get("token");
  const [form, setForm] = useState({ password: "", confirm: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirm) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/reset-password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, new_password: form.password }),
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
        setSuccess(true);
      }
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <AuthLayout
        variant="forgot"
        title="Invalid link"
        subtitle="This reset link is missing its token."
      >
        <Link href="/forgot-password" className={`${btnPrimary} block w-full`}>
          Request a new link
        </Link>
      </AuthLayout>
    );
  }

  if (success) {
    return (
      <AuthLayout
        variant="forgot"
        title="Password updated 🎉"
        subtitle="You can now log in with your new password."
      >
        <Link href="/login" className={`${btnPrimary} block w-full`}>
          Go to login
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      variant="forgot"
      title="Set a new password"
      subtitle="Choose a password you haven't used before."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <PasswordInput
          name="password"
          placeholder="New password (min 8 characters)"
          value={form.password}
          onChange={handleChange}
          required
          minLength={8}
          maxLength={72}
        />
        <PasswordInput
          name="confirm"
          placeholder="Confirm new password"
          value={form.confirm}
          onChange={handleChange}
          required
          minLength={8}
          maxLength={72}
        />
        {error && (
          <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
            {error}
            {error.toLowerCase().includes("expired") && (
              <>
                {" "}
                <Link
                  href="/forgot-password"
                  className="font-semibold underline"
                >
                  Request a new link
                </Link>
              </>
            )}
          </p>
        )}
        <button
          type="submit"
          disabled={loading}
          className={`${btnPrimary} w-full`}
        >
          {loading ? "Updating..." : "Update password"}
        </button>
      </form>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetContent />
    </Suspense>
  );
}
