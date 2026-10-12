"use client";
import { useState } from "react";
import Link from "next/link";
import { PageHeader, Label, btnGreen, btnOutline } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { categories } from "@/lib/data";

export default function NewProductPage() {
  const [done, setDone] = useState(false);

  return (
    <main>
      <PageHeader tag="// vendor_console" title="Add product" />
      <section className="mx-auto max-w-2xl px-6 py-10">
        {done ? (
          <div className="rounded-xl border border-emerald-400/30 bg-emerald-400/5 p-8 text-center">
            <p className="font-code text-sm text-emerald-400">
              ✔ Product saved (demo only)
            </p>
            <Link href="/vendor" className={`${btnGreen} mt-6`}>
              Back to dashboard
            </Link>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setDone(true);
            }}
            className="space-y-4"
          >
            <input placeholder="Product name" required className={inputClass} />
            <div className="grid gap-4 sm:grid-cols-2">
              <select required defaultValue="" className={inputClass}>
                <option value="" disabled>
                  Category
                </option>
                {categories.map((c) => (
                  <option key={c.name}>{c.name}</option>
                ))}
              </select>
              <input
                type="number"
                min="0"
                placeholder="Price"
                required
                className={inputClass}
              />
            </div>
            <input
              type="number"
              min="0"
              placeholder="Stock quantity"
              required
              className={inputClass}
            />
            <textarea
              rows={4}
              placeholder="Description and specs"
              required
              className={inputClass}
            />
            <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center">
              <Label>Product images upload comes later</Label>
            </div>
            <div className="flex gap-3">
              <button className={`${btnGreen} flex-1`}>Save product</button>
              <Link href="/vendor" className={btnOutline}>
                Cancel
              </Link>
            </div>
          </form>
        )}
      </section>
    </main>
  );
}
