import Link from "next/link";
import { notFound } from "next/navigation";
import {
  PageHeader,
  Icon,
  Label,
  Status,
  btnOutline,
  wrap,
} from "@/components/ui";
import { orders, products, money } from "@/lib/data";

const timeline = ["Placed", "Packed", "Shipped", "Delivered"];

export default async function OrderDetail({ params }) {
  const { id } = await params;
  const order = orders.find((o) => o.id === id);
  if (!order) notFound();

  return (
    <main>
      <PageHeader tag={`// order ${order.id}`} title="Order detail">
        Placed on {order.date}
      </PageHeader>
      <section className={`${wrap} space-y-8 py-10`}>
        <div className="flex items-center justify-between">
          <Status status={order.status} />
          <Link href="/orders" className={btnOutline}>
            Back to orders
          </Link>
        </div>

        {/* Timeline */}
        <div className="font-code grid grid-cols-2 overflow-hidden rounded-lg border border-slate-700 text-xs sm:grid-cols-4">
          {timeline.map((t, i) => (
            <div
              key={t}
              className={`px-4 py-3 ${i < order.step ? "bg-emerald-400/10 text-emerald-300" : "text-slate-500"}`}
            >
              {i < order.step ? "✔" : "○"} {t}
            </div>
          ))}
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            {order.items.map((i) => {
              const p = products.find((x) => x.id === i.id);
              return (
                <div
                  key={i.id}
                  className="card group flex items-center gap-5 p-4"
                >
                  <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-slate-950/60">
                    <Icon name={p.sticker} className="text-3xl" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-white">{p.name}</p>
                    <Label>Qty {i.qty}</Label>
                  </div>
                  <p className="font-code font-bold text-cyan-400">
                    {money(p.price * i.qty)}
                  </p>
                </div>
              );
            })}
          </div>
          <aside className="h-fit rounded-xl border border-slate-800 bg-slate-900/60 p-6">
            <p className="font-code text-sm text-cyan-400">// summary</p>
            <div className="font-code mt-4 flex justify-between text-base font-bold text-white">
              <span>Total</span>
              <span>{money(order.total)}</span>
            </div>
            <button className={`${btnOutline} mt-6 w-full`}>
              Download invoice
            </button>
          </aside>
        </div>
      </section>
    </main>
  );
}
