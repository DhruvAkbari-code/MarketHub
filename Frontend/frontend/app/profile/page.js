"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Label, Pill, btnPrimary, btnOutline, wrap } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import PasswordInput from "@/components/PasswordInput";

const tabs = [
  { id: "details", label: "Personal details", icon: "👤" },
  { id: "addresses", label: "Addresses", icon: "📍" },
  { id: "security", label: "Password", icon: "🔒" },
];

function BigAvatar({ user }) {
  if (user.profile_picture) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={user.profile_picture}
        alt={user.username}
        referrerPolicy="no-referrer"
        className="h-24 w-24 rounded-full border-2 border-cyan-400/60 object-cover shadow-lg shadow-cyan-500/10"
      />
    );
  }
  return (
    <span className="font-code flex h-24 w-24 items-center justify-center rounded-full border-2 border-cyan-400/60 bg-cyan-400/10 text-4xl font-bold text-cyan-300">
      {user.username?.[0]?.toUpperCase() || "?"}
    </span>
  );
}

function ChangePasswordForm() {
  const [form, setForm] = useState({ current: "", next: "", confirm: "" });
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [saving, setSaving] = useState(false);

  function handleChange(e) {
    setDone(false);
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setDone(false);

    if (form.next !== form.confirm) {
      setError("New passwords do not match");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/change-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            current_password: form.current,
            new_password: form.next,
          }),
        },
      );
      const data = await res.json();
      if (!res.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Could not change password",
        );
        return;
      }
      setForm({ current: "", next: "", confirm: "" });
      setDone(true);
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/60 p-6"
    >
      <p className="font-code text-sm text-cyan-400">// change_password</p>

      <div>
        <Label className="mb-1">Current password</Label>
        <PasswordInput
          name="current"
          placeholder="Current password"
          value={form.current}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <Label className="mb-1">New password (min 8 characters)</Label>
        <PasswordInput
          name="next"
          placeholder="New password"
          value={form.next}
          onChange={handleChange}
          required
          minLength={8}
          maxLength={72}
        />
      </div>
      <div>
        <Label className="mb-1">Confirm new password</Label>
        <PasswordInput
          name="confirm"
          placeholder="Confirm new password"
          value={form.confirm}
          onChange={handleChange}
          required
          minLength={8}
          maxLength={72}
        />
      </div>

      {error && (
        <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
          {error}
        </p>
      )}
      {done && (
        <p className="font-code text-xs text-emerald-400">✔ Password updated</p>
      )}
      <button type="submit" disabled={saving} className={btnPrimary}>
        {saving ? "Updating..." : "Update password"}
      </button>
    </form>
  );
}

const emptyAddress = {
  label: "Home",
  full_name: "",
  phone: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  postal_code: "",
  is_default: false,
};

function AddressBook() {
  const api = `${process.env.NEXT_PUBLIC_API_URL}/api/auth/addresses`;
  const headers = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
  });

  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null); // null = closed, "new" or an id
  const [form, setForm] = useState(emptyAddress);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const res = await fetch(api, { headers: headers() });
      if (res.ok) setList(await res.json());
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openNew() {
    setError("");
    setForm({ ...emptyAddress, is_default: list.length === 0 });
    setEditing("new");
  }

  function openEdit(a) {
    setError("");
    setForm({ ...a, line2: a.line2 || "" });
    setEditing(a.id);
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleDigits(max) {
    return (e) =>
      setForm({
        ...form,
        [e.target.name]: e.target.value.replace(/\D/g, "").slice(0, max),
      });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const isNew = editing === "new";
      const res = await fetch(isNew ? api : `${api}/${editing}`, {
        method: isNew ? "POST" : "PUT",
        headers: headers(),
        body: JSON.stringify({ ...form, line2: form.line2 || null }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Could not save address",
        );
        return;
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (!confirm("Remove this address?")) return;
    await fetch(`${api}/${id}`, { method: "DELETE", headers: headers() });
    load();
  }

  async function makeDefault(id) {
    await fetch(`${api}/${id}/default`, { method: "POST", headers: headers() });
    load();
  }

  if (loading) return <Label>loading...</Label>;

  if (editing) {
    return (
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6"
      >
        <p className="font-code text-sm text-cyan-400">
          {editing === "new" ? "// add_address" : "// edit_address"}
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label className="mb-1">Label (Home, Office...)</Label>
            <input
              name="label"
              value={form.label}
              onChange={handleChange}
              required
              maxLength={30}
              className={inputClass}
            />
          </div>
          <div>
            <Label className="mb-1">Full name</Label>
            <input
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              required
              minLength={2}
              maxLength={100}
              className={inputClass}
            />
          </div>
        </div>

        <div>
          <Label className="mb-1">Phone (10 digits)</Label>
          <input
            name="phone"
            type="tel"
            inputMode="numeric"
            value={form.phone}
            onChange={handleDigits(10)}
            required
            minLength={10}
            maxLength={10}
            className={inputClass}
          />
        </div>

        <div>
          <Label className="mb-1">Address line 1</Label>
          <input
            name="line1"
            value={form.line1}
            onChange={handleChange}
            required
            minLength={3}
            maxLength={150}
            className={inputClass}
          />
        </div>
        <div>
          <Label className="mb-1">Address line 2 (optional)</Label>
          <input
            name="line2"
            value={form.line2}
            onChange={handleChange}
            maxLength={150}
            className={inputClass}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <Label className="mb-1">City</Label>
            <input
              name="city"
              value={form.city}
              onChange={handleChange}
              required
              className={inputClass}
            />
          </div>
          <div>
            <Label className="mb-1">State</Label>
            <input
              name="state"
              value={form.state}
              onChange={handleChange}
              required
              className={inputClass}
            />
          </div>
          <div>
            <Label className="mb-1">Postal code (6 digits)</Label>
            <input
              name="postal_code"
              inputMode="numeric"
              value={form.postal_code}
              onChange={handleDigits(6)}
              required
              minLength={6}
              maxLength={6}
              className={inputClass}
            />
          </div>
        </div>

        <label className="font-code flex items-center gap-2 text-xs text-slate-300">
          <input
            type="checkbox"
            checked={form.is_default}
            onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
          />
          Use as my default address
        </label>

        {error && (
          <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
            {error}
          </p>
        )}
        <div className="flex gap-3">
          <button type="submit" disabled={saving} className={btnPrimary}>
            {saving ? "Saving..." : "Save address"}
          </button>
          <button
            type="button"
            onClick={() => setEditing(null)}
            className={btnOutline}
          >
            Cancel
          </button>
        </div>
      </form>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="font-code text-sm text-cyan-400">
          // addresses ({list.length}/10)
        </p>
        <button
          onClick={openNew}
          disabled={list.length >= 10}
          className={`${btnPrimary} disabled:opacity-50`}
        >
          + Add address
        </button>
      </div>

      {error && (
        <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
          {error}
        </p>
      )}

      {list.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center">
          <p className="font-code text-sm text-slate-400">
            No addresses yet. Add your first one.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {list.map((a) => (
            <div
              key={a.id}
              className={`rounded-xl border p-5 ${
                a.is_default
                  ? "border-cyan-400/60 bg-cyan-400/5"
                  : "border-slate-800 bg-slate-900/60"
              }`}
            >
              <div className="flex items-center justify-between">
                <p className="font-semibold text-white">{a.label}</p>
                {a.is_default && <Pill>default</Pill>}
              </div>
              <p className="mt-2 text-sm text-slate-300">{a.full_name}</p>
              <p className="text-sm text-slate-400">
                {a.line1}
                {a.line2 ? `, ${a.line2}` : ""}
              </p>
              <p className="text-sm text-slate-400">
                {a.city}, {a.state} {a.postal_code}
              </p>
              <p className="font-code mt-1 text-xs text-slate-500">{a.phone}</p>

              <div className="font-code mt-4 flex flex-wrap gap-4 text-xs">
                <button
                  onClick={() => openEdit(a)}
                  className="text-cyan-400 hover:underline"
                >
                  edit
                </button>
                {!a.is_default && (
                  <button
                    onClick={() => makeDefault(a.id)}
                    className="text-emerald-400 hover:underline"
                  >
                    make default
                  </button>
                )}
                <button
                  onClick={() => remove(a.id)}
                  className="text-rose-400 hover:underline"
                >
                  remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ProfilePage() {
  const router = useRouter();
  const [tab, setTab] = useState("details");
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({ username: "", phone: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/login");
        return;
      }
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`,
          { headers: { Authorization: `Bearer ${token}` } },
        );
        if (res.status === 401) {
          localStorage.removeItem("access_token");
          window.dispatchEvent(new Event("auth-change"));
          router.replace("/login");
          return;
        }
        const data = await res.json();
        setUser(data);
        setForm({ username: data.username, phone: data.phone || "" });
      } catch (err) {
        setError("Cannot reach the server");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [router]);

  function handleChange(e) {
    setSaved(false);
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  // phone: digits only, max 10
  function handlePhone(e) {
    setSaved(false);
    const digits = e.target.value.replace(/\D/g, "").slice(0, 10);
    setForm({ ...form, phone: digits });
  }

  async function handleSave(e) {
    e.preventDefault();
    setError("");
    setSaved(false);

    if (form.phone && form.phone.length !== 10) {
      setError("Phone number must be exactly 10 digits");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            username: form.username,
            phone: form.phone || null,
          }),
        },
      );
      const data = await res.json();
      if (!res.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Could not save changes",
        );
        return;
      }
      setUser(data);
      setForm({ username: data.username, phone: data.phone || "" });
      setSaved(true);
      window.dispatchEvent(new Event("auth-change"));
    } catch (err) {
      setError("Cannot reach the server");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <main className={`${wrap} py-16`}>
        <Label>loading...</Label>
      </main>
    );
  }

  if (!user) {
    return (
      <main className={`${wrap} py-16`}>
        <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
          {error || "Could not load your profile"}
        </p>
      </main>
    );
  }

  return (
    <main>
      {/* Header card */}
      <div className="bg-grid border-b border-slate-800">
        <div
          className={`${wrap} flex flex-col items-center gap-6 py-12 sm:flex-row`}
        >
          <BigAvatar user={user} />
          <div className="text-center sm:text-left">
            <p className="font-code text-sm text-cyan-400">// account</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight text-white">
              {user.username}
            </h1>
            <p className="font-code mt-1 text-sm text-slate-400">
              {user.email}
            </p>
            <div className="mt-3 flex flex-wrap justify-center gap-2 sm:justify-start">
              <Pill>{user.role}</Pill>
              <span
                className={`font-code inline-block rounded-full border px-3 py-1 text-xs ${
                  user.email_verified
                    ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-300"
                    : "border-amber-400/40 bg-amber-400/10 text-amber-300"
                }`}
              >
                {user.email_verified
                  ? "✔ email verified"
                  : "email not verified"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <section className={`${wrap} grid gap-8 py-10 lg:grid-cols-4`}>
        {/* Side menu */}
        <nav className="flex gap-2 overflow-x-auto lg:flex-col">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`font-code flex items-center gap-3 whitespace-nowrap rounded-lg border px-4 py-3 text-left text-sm transition ${
                tab === t.id
                  ? "border-cyan-400 bg-cyan-400/10 text-cyan-300"
                  : "border-slate-800 bg-slate-900/60 text-slate-400 hover:border-cyan-400/50 hover:text-cyan-400"
              }`}
            >
              <span>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>

        {/* Panel */}
        <div className="lg:col-span-3">
          {tab === "details" && (
            <form
              onSubmit={handleSave}
              className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/60 p-6"
            >
              <p className="font-code text-sm text-cyan-400">
                // personal_details
              </p>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <Label className="mb-1">Username</Label>
                  <input
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    required
                    minLength={3}
                    maxLength={30}
                    pattern="[A-Za-z0-9_]+"
                    title="Letters, numbers and underscores only"
                    className={inputClass}
                  />
                </div>
                <div>
                  <Label className="mb-1">Phone (10 digits)</Label>
                  <input
                    name="phone"
                    type="tel"
                    inputMode="numeric"
                    placeholder="9876543210"
                    value={form.phone}
                    onChange={handlePhone}
                    maxLength={10}
                    className={inputClass}
                  />
                </div>
              </div>

              <div>
                <Label className="mb-1">Email (cannot be changed)</Label>
                <input
                  value={user.email}
                  disabled
                  className={`${inputClass} cursor-not-allowed opacity-60`}
                />
              </div>

              {error && (
                <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-400">
                  {error}
                </p>
              )}
              {saved && (
                <p className="font-code text-xs text-emerald-400">
                  ✔ Changes saved
                </p>
              )}
              <button type="submit" disabled={saving} className={btnPrimary}>
                {saving ? "Saving..." : "Save changes"}
              </button>
            </form>
          )}

          {tab === "addresses" && <AddressBook />}
          {tab === "security" && <ChangePasswordForm />}
        </div>
      </section>
    </main>
  );
}
