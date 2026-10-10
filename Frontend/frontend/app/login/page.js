"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/AuthLayout";
import GoogleButton from "@/components/GoogleButton";
import PasswordInput from "@/components/PasswordInput";
import { Or, btnPrimary } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: form.email,
            password: form.password,
          }),
        },
      );
      const data = await res.json();
      if (!res.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Login failed",
        );
        return;
      }
      localStorage.setItem("access_token", data.access_token);
      window.dispatchEvent(new Event("auth-change"));
      router.replace("/");
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      variant="login"
      title="Welcome back"
      subtitle="Log in to continue to your Market Hub account."
    >
      <GoogleButton text="signin_with" onError={setError} />

      <Or />

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          name="email"
          placeholder="Email address"
          value={form.email}
          onChange={handleChange}
          required
          className={inputClass}
        />
        <PasswordInput
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <div className="text-right">
          <Link
            href="/forgot-password"
            className="text-xs font-semibold text-cyan-400 hover:underline"
          >
            Forgot password?
          </Link>
        </div>
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
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        New to Market Hub?{" "}
        <Link
          href="/register"
          className="font-semibold text-cyan-400 hover:underline"
        >
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
