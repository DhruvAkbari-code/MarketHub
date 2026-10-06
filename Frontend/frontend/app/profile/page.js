"use client";
import { useState } from "react";
import { PageHeader, btnPrimary, btnOutline, wrap } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";

export default function ProfilePage() {
  const [form, setForm] = useState({
    username: "dev_user",
    email: "dev@example.com",
    phone: "",
  });
  const [saved, setSaved] = useState(false);

  function handleChange(e) {
    setSaved(false);
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  return (
    <main>
      <PageHeader tag="// account" title="Your profile" />
      <section className={`${wrap} grid gap-8 py-10 lg:grid-cols-2`}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setSaved(true);
          }}
          className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6"
        >
          <p className="font-code text-sm text-cyan-400">// details</p>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            className={inputClass}
          />
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            className={inputClass}
          />
          <input
            type="tel"
            name="phone"
            placeholder="Phone"
            value={form.phone}
            onChange={handleChange}
            className={inputClass}
          />
          {saved && (
            <p className="font-code text-xs text-emerald-400">
              ✔ Saved (demo only)
            </p>
          )}
          <button className={`${btnPrimary} w-full`}>Save changes</button>
        </form>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="font-code text-sm text-cyan-400">// addresses</p>
          <div className="mt-4 space-y-3">
            {[
              "Home — 12 Stack Street, Bangalore",
              "Office — 4 Commit Road, Pune",
            ].map((a) => (
              <div
                key={a}
                className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/60 p-3"
              >
                <span className="font-code text-xs text-slate-300">{a}</span>
                <button className="font-code text-xs text-cyan-400 hover:underline">
                  edit
                </button>
              </div>
            ))}
          </div>
          <button className={`${btnOutline} mt-4`}>+ Add address</button>
        </div>
      </section>
    </main>
  );
}
