"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import GoogleButton from "@/components/GoogleButton";
import PasswordInput from "@/components/PasswordInput";
import { Or, btnPrimary } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    phone: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: form.email,
            username: form.username,
            password: form.password,
            phone: form.phone || null,
          }),
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

  if (success) {
    return (
      <AuthLayout
        variant="register"
        title="Account created 🎉"
        subtitle="Welcome to Market Hub. You're ready to go."
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
      title="Create your account"
      subtitle="Join Market Hub and get the best gear for your setup."
    >
      <GoogleButton
        label="Sign up with Google"
        onClick={() => alert("Google sign-in is coming soon")}
      />
      <Or />
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
          minLength={3}
          maxLength={30}
          pattern="[A-Za-z0-9_]+"
          title="Letters, numbers and underscores only"
          className={inputClass}
        />
        <input
          type="email"
          name="email"
          placeholder="Email address"
          value={form.email}
          onChange={handleChange}
          required
          className={inputClass}
        />
        <input
          type="tel"
          name="phone"
          placeholder="Phone (optional, e.g. +919876543210)"
          value={form.phone}
          onChange={handleChange}
          className={inputClass}
        />
        <PasswordInput
          name="password"
          placeholder="Password (min 8 characters)"
          value={form.password}
          onChange={handleChange}
          required
          minLength={8}
          maxLength={72}
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
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-semibold text-cyan-400 hover:underline"
        >
          Log in
        </Link>
      </p>
    </AuthLayout>
  );
}
