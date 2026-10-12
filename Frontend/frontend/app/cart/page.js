"use client";
import { useState } from "react";
import Link from "next/link";
import {
  PageHeader,
  Icon,
  Label,
  btnPrimary,
  btnOutline,
  wrap,
} from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { cartItems, products, money } from "@/lib/data";

export default function CartPage() {
  const [items, setItems] = useState(cartItems);
  const [coupon, setCoupon] = useState("");

  const rows = items.map((i) => ({
    ...products.find((p) => p.id === i.id),
    qty: i.qty,
  }));
  const subtotal = rows.reduce((s, r) => s + r.price * r.qty, 0);
  const shipping = subtotal === 0 || subtotal > 100 ? 0 : 9;
  const total = subtotal + shipping;

  function change(id, delta) {
    setItems(
      items.map((i) =>
        i.id === id ? { ...i, qty: Math.max(1, i.qty + delta) } : i,
      ),
    );
  }
  function remove(id) {
    setItems(items.filter((i) => i.id !== id));
  }

  return (
    <main>
      <PageHeader tag="// cart" title="Your cart" />
      <section className={`${wrap} grid gap-8 py-10 lg:grid-cols-3`}>
        <div className="space-y-4 lg:col-span-2">
          {rows.length === 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-10 text-center">
              <p className="font-code text-sm text-slate-400">
                Your cart is empty.
              </p>
              <Link href="/products" className={`${btnPrimary} mt-6`}>
                Browse gear
              </Link>
            </div>
          )}
          {rows.map((r) => (
            <div key={r.id} className="card group flex items-center gap-5 p-4">
              <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-lg bg-slate-950/60">
                <Icon name={r.sticker} className="text-4xl" />
              </div>
              <div className="flex-1">
                <Label>{r.category}</Label>
                <p className="font-semibold text-white">{r.name}</p>
                <button
                  onClick={() => remove(r.id)}
                  className="font-code mt-1 text-xs text-rose-400 hover:underline"
                >
                  remove
                </button>
              </div>
              <div className="font-code flex items-center rounded-lg border border-slate-700 text-white">
                <button
                  onClick={() => change(r.id, -1)}
                  className="px-3 py-1 hover:text-cyan-400"
                >
                  −
                </button>
                <span className="w-8 text-center">{r.qty}</span>
                <button
                  onClick={() => change(r.id, 1)}
                  className="px-3 py-1 hover:text-cyan-400"
                >
                  +
                </button>
              </div>
              <p className="font-code w-20 text-right font-bold text-cyan-400">
                {money(r.price * r.qty)}
              </p>
            </div>
          ))}
        </div>

        <aside className="h-fit rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="font-code text-sm text-cyan-400">// order_summary</p>
          <div className="font-code mt-4 space-y-3 text-sm text-slate-300">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{money(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Shipping</span>
              <span>{shipping === 0 ? "Free" : money(shipping)}</span>
            </div>
            <div className="flex justify-between border-t border-slate-800 pt-3 text-base font-bold text-white">
              <span>Total</span>
              <span>{money(total)}</span>
            </div>
          </div>
          <div className="mt-6 flex gap-2">
            <input
              value={coupon}
              onChange={(e) => setCoupon(e.target.value)}
              placeholder="Coupon code"
              className={inputClass}
            />
            <button className={`${btnOutline} !px-4`}>Apply</button>
          </div>
          <Link href="/checkout" className={`${btnPrimary} mt-6 block`}>
            Checkout
          </Link>
        </aside>
      </section>
    </main>
  );
}
