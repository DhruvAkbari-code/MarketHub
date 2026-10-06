"use client";
import { useState } from "react";
import { PageHeader, Label, Bar, Status, wrap } from "@/components/ui";

const stats = [
  { label: "Users", value: "3,204", bar: 70 },
  { label: "Vendors", value: "58", bar: 40 },
  { label: "Orders today", value: "212", bar: 85 },
  { label: "Open reports", value: "3", bar: 12 },
];

const users = [
  { name: "dev_aria", email: "aria@example.com", role: "customer" },
  { name: "keyforge", email: "hello@keyforge.dev", role: "vendor" },
  { name: "null_pointer", email: "np@example.com", role: "customer" },
];

const tableBox =
  "mt-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60";
const th = "p-3 font-medium";

export default function AdminDashboard() {
  const [apps, setApps] = useState([
    {
      id: 1,
      store: "BitBench",
      owner: "Sam K.",
      category: "Circuits",
      status: "Pending",
    },
    {
      id: 2,
      store: "TurboToys",
      owner: "Lena R.",
      category: "RC Cars",
      status: "Pending",
    },
    {
      id: 3,
      store: "PixelPeak",
      owner: "Omar T.",
      category: "Screens",
      status: "Approved",
    },
  ]);

  function setStatus(id, status) {
    setApps(apps.map((a) => (a.id === id ? { ...a, status } : a)));
  }

  return (
    <main>
      <PageHeader tag="// admin_console" title="Platform overview" />
      <section className={`${wrap} space-y-10 py-10`}>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="card p-5">
              <Label>{s.label}</Label>
              <p className="font-code mt-2 text-3xl font-bold text-white">
                {s.value}
              </p>
              <div className="mt-4">
                <Bar value={s.bar} />
              </div>
            </div>
          ))}
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">Vendor applications</h2>
          <div className={tableBox}>
            <table className="font-code w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-slate-500">
                <tr>
                  <th className={th}>Store</th>
                  <th className={th}>Owner</th>
                  <th className={th}>Category</th>
                  <th className={th}>Status</th>
                  <th className={th}>Action</th>
                </tr>
              </thead>
              <tbody>
                {apps.map((a) => (
                  <tr key={a.id} className="border-b border-slate-800/60">
                    <td className="p-3 font-semibold text-white">{a.store}</td>
                    <td className="p-3">{a.owner}</td>
                    <td className="p-3">{a.category}</td>
                    <td className="p-3">
                      <Status status={a.status} />
                    </td>
                    <td className="space-x-4 p-3">
                      {a.status === "Pending" && (
                        <>
                          <button
                            onClick={() => setStatus(a.id, "Approved")}
                            className="text-emerald-400 hover:underline"
                          >
                            approve
                          </button>
                          <button
                            onClick={() => setStatus(a.id, "Rejected")}
                            className="text-rose-400 hover:underline"
                          >
                            reject
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">Users</h2>
          <div className={tableBox}>
            <table className="font-code w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-slate-500">
                <tr>
                  <th className={th}>Username</th>
                  <th className={th}>Email</th>
                  <th className={th}>Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.name} className="border-b border-slate-800/60">
                    <td className="p-3 font-semibold text-white">{u.name}</td>
                    <td className="p-3">{u.email}</td>
                    <td className="p-3">{u.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}
