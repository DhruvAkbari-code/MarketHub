"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import PasswordInput from "@/components/PasswordInput";
import { btnGreen, Label } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { categories } from "@/lib/data";

export default function BecomeVendorPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    phone: "",
    password: "",
    storeName: "",
    category: "",
    website: "",
    about: "",
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/register/vendor`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: form.username,
            email: form.email,
            phone: form.phone || null,
            password: form.password,
            store_name: form.storeName,
            category: form.category,
            website: form.website || null,
            about: form.about,
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
        variant="vendor"
        title="Check your email 📬"
        subtitle="Verify your email, then log in. Your store goes live once we approve your application."
      >
        <Link href="/login" className={`${btnGreen} block w-full`}>
          Go to login
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      variant="vendor"
      wide
      title="Create a vendor account"
      subtitle="Set up your login and tell us about your store."
    >
      {/* Role switch */}
      <div className="font-code mb-6 grid grid-cols-2 overflow-hidden rounded-lg border border-slate-700 text-xs">
        <Link
          href="/register"
          className="px-4 py-2.5 text-center text-slate-400 transition hover:text-cyan-400"
        >
          Customer
        </Link>
        <span className="bg-emerald-400 px-4 py-2.5 text-center font-semibold text-slate-950">
          Vendor
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Label className="!text-emerald-400">// account</Label>
        <div className="grid gap-4 sm:grid-cols-2">
          <input
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
            type="tel"
            name="phone"
            placeholder="Phone (optional)"
            value={form.phone}
            onChange={handleChange}
            className={inputClass}
          />
        </div>
        <input
          type="email"
          name="email"
          placeholder="Business email"
          value={form.email}
          onChange={handleChange}
          required
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

        <Label className="!text-emerald-400 pt-2">// store</Label>
        <div className="grid gap-4 sm:grid-cols-2">
          <input
            name="storeName"
            placeholder="Store name"
            value={form.storeName}
            onChange={handleChange}
            required
            className={inputClass}
          />
          <select
            name="category"
            value={form.category}
            onChange={handleChange}
            required
            className={inputClass}
          >
            <option value="" disabled>
              Main category
            </option>
            {categories.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <input
          type="url"
          name="website"
          placeholder="Website or GitHub (optional)"
          value={form.website}
          onChange={handleChange}
          className={inputClass}
        />
        <textarea
          name="about"
          placeholder="Tell us about your products..."
          value={form.about}
          onChange={handleChange}
          required
          rows={3}
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
          className={`${btnGreen} w-full disabled:opacity-60`}
        >
          {loading ? "Creating account..." : "Create vendor account"}
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
