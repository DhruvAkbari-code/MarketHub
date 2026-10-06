import Link from "next/link";
import { Label, btnPrimary, btnOutline } from "@/components/ui";

export default async function PaymentCallback({ searchParams }) {
  const { status } = await searchParams;
  const ok = status !== "failed";

  return (
    <main className="bg-grid flex min-h-[calc(100vh-73px)] items-center justify-center px-6 py-16">
      <div className="anim-fade-up w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900/80 p-10 text-center shadow-2xl shadow-cyan-500/5">
        <div className="anim-float text-6xl">{ok ? "🎉" : "⚠️"}</div>
        <Label
          className={`mt-6 ${ok ? "!text-emerald-400" : "!text-rose-400"}`}
        >
          {ok ? "// payment_success" : "// payment_failed"}
        </Label>
        <h1 className="mt-2 text-3xl font-bold text-white">
          {ok ? "Order confirmed" : "Payment failed"}
        </h1>
        <p className="mt-3 text-sm text-slate-400">
          {ok
            ? "Thanks for your order. A confirmation email and invoice are on their way."
            : "Your payment did not go through. You have not been charged. Please try again."}
        </p>
        {ok && (
          <p className="font-code mt-4 text-sm font-bold text-cyan-400">
            ORDER MH-1043
          </p>
        )}
        <div className="mt-8 flex justify-center gap-3">
          <Link href={ok ? "/orders" : "/checkout"} className={btnPrimary}>
            {ok ? "View orders" : "Try again"}
          </Link>
          <Link href="/products" className={btnOutline}>
            Keep shopping
          </Link>
        </div>
      </div>
    </main>
  );
}
