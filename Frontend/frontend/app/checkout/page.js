"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  PageHeader,
  Label,
  btnPrimary,
  btnOutline,
  wrap,
} from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { cartItems, products, money } from "@/lib/data";

const steps = ["Address", "Shipping", "Payment"];

export default function CheckoutPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [ship, setShip] = useState("standard");

  const rows = cartItems.map((c) => ({
    ...products.find((p) => p.id === c.id),
    qty: c.qty,
  }));
  const subtotal = rows.reduce((s, r) => s + r.price * r.qty, 0);
  const shipping = ship === "express" ? 19 : 0;

  function next(e) {
    e.preventDefault();
    if (step < 2) setStep(step + 1);
    else router.push("/payment/callback?status=success"); // payment gateway comes in a later step
  }

  return (
    <main>
      <PageHeader tag="// checkout" title="Checkout" />
      <section className={`${wrap} grid gap-8 py-10 lg:grid-cols-3`}>
        <div className="lg:col-span-2">
          {/* Stepper */}
          <div className="font-code grid grid-cols-3 overflow-hidden rounded-lg border border-slate-700 text-xs">
            {steps.map((s, i) => (
              <div
                key={s}
                className={`px-4 py-3 ${
                  i === step
                    ? "bg-cyan-400 font-semibold text-slate-950"
                    : i < step
                      ? "bg-emerald-400/10 text-emerald-300"
                      : "text-slate-500"
                }`}
              >
                {i < step ? "✔" : `0${i + 1}`} {s}
              </div>
            ))}
          </div>

          <form onSubmit={next} className="mt-6 space-y-4">
            {step === 0 && (
              <>
                <div className="grid gap-4 sm:grid-cols-2">
                  <input
                    placeholder="Full name"
                    required
                    className={inputClass}
                  />
                  <input
                    type="tel"
                    placeholder="Phone"
                    required
                    className={inputClass}
                  />
                </div>
                <input
                  placeholder="Street address"
                  required
                  className={inputClass}
                />
                <div className="grid gap-4 sm:grid-cols-2">
                  <input placeholder="City" required className={inputClass} />
                  <input
                    placeholder="Postal code"
                    required
                    className={inputClass}
                  />
                </div>
              </>
            )}

            {step === 1 && (
              <>
                {[
                  ["standard", "Standard delivery", "4-6 days", "Free"],
                  ["express", "Express delivery", "1-2 days", "$19"],
                ].map(([value, name, eta, price]) => (
                  <label
                    key={value}
                    className={`flex cursor-pointer items-center justify-between rounded-xl border p-4 transition ${
                      ship === value
                        ? "border-cyan-400 bg-cyan-400/5"
                        : "border-slate-800 bg-slate-900/60"
                    }`}
                  >
                    <span className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="ship"
                        checked={ship === value}
                        onChange={() => setShip(value)}
                      />
                      <span>
                        <span className="block font-semibold text-white">
                          {name}
                        </span>
                        <Label>{eta}</Label>
                      </span>
                    </span>
                    <span className="font-code font-bold text-cyan-400">
                      {price}
                    </span>
                  </label>
                ))}
              </>
            )}

            {step === 2 && (
              <>
                <Label>
                  Demo form only. Real payments will go through the payment
                  service later.
                </Label>
                <input
                  placeholder="Name on card"
                  required
                  className={inputClass}
                />
                <input
                  placeholder="Card number"
                  required
                  inputMode="numeric"
                  className={inputClass}
                />
                <div className="grid gap-4 sm:grid-cols-2">
                  <input
                    placeholder="MM / YY"
                    required
                    className={inputClass}
                  />
                  <input placeholder="CVC" required className={inputClass} />
                </div>
              </>
            )}

            <div className="flex gap-3">
              {step > 0 && (
                <button
                  type="button"
                  onClick={() => setStep(step - 1)}
                  className={btnOutline}
                >
                  Back
                </button>
              )}
              <button type="submit" className={`${btnPrimary} flex-1`}>
                {step < 2 ? "Continue" : `Pay ${money(subtotal + shipping)}`}
              </button>
            </div>
          </form>
        </div>

        <aside className="h-fit rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="font-code text-sm text-cyan-400">// your_order</p>
          <div className="font-code mt-4 space-y-3 text-sm text-slate-300">
            {rows.map((r) => (
              <div key={r.id} className="flex justify-between gap-4">
                <span>
                  {r.qty} x {r.name}
                </span>
                <span>{money(r.price * r.qty)}</span>
              </div>
            ))}
            <div className="flex justify-between border-t border-slate-800 pt-3">
              <span>Shipping</span>
              <span>{shipping ? money(shipping) : "Free"}</span>
            </div>
            <div className="flex justify-between text-base font-bold text-white">
              <span>Total</span>
              <span>{money(subtotal + shipping)}</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
