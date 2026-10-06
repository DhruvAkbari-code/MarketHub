import Link from "next/link";
import { PageHeader, Icon, Label, Status, wrap } from "@/components/ui";
import { orders, products, money } from "@/lib/data";

export default function OrdersPage() {
  return (
    <main>
      <PageHeader tag="// orders" title="Order history" />
      <section className={`${wrap} space-y-4 py-10`}>
        {orders.map((o) => {
          const first = products.find((p) => p.id === o.items[0].id);
          return (
            <Link
              key={o.id}
              href={`/orders/${o.id}`}
              className="card group flex items-center gap-5 p-4"
            >
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-slate-950/60">
                <Icon name={first.sticker} className="text-3xl" />
              </div>
              <div className="flex-1">
                <p className="font-code text-sm font-bold text-white">{o.id}</p>
                <Label>
                  {o.date} · {o.items.length} item(s)
                </Label>
              </div>
              <Status status={o.status} />
              <p className="font-code w-20 text-right font-bold text-cyan-400">
                {money(o.total)}
              </p>
            </Link>
          );
        })}
      </section>
    </main>
  );
}
