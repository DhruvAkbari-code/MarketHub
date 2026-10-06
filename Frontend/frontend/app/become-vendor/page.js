"use client";
import { useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/AuthLayout";
import { btnGreen } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { categories } from "@/lib/data";

export default function BecomeVendorPage() {
  const [form, setForm] = useState({
    storeName: "",
    fullName: "",
    email: "",
    phone: "",
    category: "",
    website: "",
    about: "",
  });
  const [submitted, setSubmitted] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    // The vendor API will be connected in a later step
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <AuthLayout
        variant="vendor"
        title="Application received 🚀"
        subtitle="Thanks for applying. We'll review your store and get back to you."
      >
        <Link href="/" className={`${btnGreen} block w-full`}>
          Back to home
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      variant="vendor"
      wide
      title="Become a vendor"
      subtitle="Tell us about your store and start selling to developers."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <input
            name="storeName"
            placeholder="Store name"
            value={form.storeName}
            onChange={handleChange}
            required
            className={inputClass}
          />
          <input
            name="fullName"
            placeholder="Your full name"
            value={form.fullName}
            onChange={handleChange}
            required
            className={inputClass}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <input
            type="email"
            name="email"
            placeholder="Business email"
            value={form.email}
            onChange={handleChange}
            required
            className={inputClass}
          />
          <input
            type="tel"
            name="phone"
            placeholder="Phone number"
            value={form.phone}
            onChange={handleChange}
            required
            className={inputClass}
          />
        </div>
        <select
          name="category"
          value={form.category}
          onChange={handleChange}
          required
          className={inputClass}
        >
          <option value="" disabled>
            What will you mainly sell?
          </option>
          {categories.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
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
          rows={4}
          className={inputClass}
        />
        <button type="submit" className={`${btnGreen} w-full`}>
          Submit application
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Just want to shop?{" "}
        <Link
          href="/register"
          className="font-semibold text-cyan-400 hover:underline"
        >
          Create a buyer account
        </Link>
      </p>
    </AuthLayout>
  );
}
