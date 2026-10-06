"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import GoogleButton from "@/components/GoogleButton";
import PasswordInput from "@/components/PasswordInput";
import { Or, btnPrimary } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    // The login API will be connected in a later step
    setMessage("Login is not connected to the backend yet.");
  }

  return (
    <AuthLayout
      variant="login"
      title="Welcome back"
      subtitle="Log in to continue to your Market Hub account."
    >
      <GoogleButton onClick={() => alert("Google sign-in is coming soon")} />
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
        {message && (
          <p className="rounded-lg bg-sky-500/10 px-3 py-2 text-sm text-sky-400">
            {message}
          </p>
        )}
        <button type="submit" className={`${btnPrimary} w-full`}>
          Log in
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
