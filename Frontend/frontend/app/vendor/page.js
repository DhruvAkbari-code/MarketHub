import Link from "next/link";
import {
  PageHeader,
  Label,
  Bar,
  Status,
  btnGreen,
  wrap,
} from "@/components/ui";
import { products, money } from "@/lib/data";

const stats = [
  { label: "Revenue", value: "$12,480", bar: 78 },
  { label: "Orders", value: "164", bar: 62 },
  { label: "Products", value: "18", bar: 45 },
  { label: "Rating", value: "4.8", bar: 96 },
];

const recent = [
  { id: "MH-1042", buyer: "dev_aria", total: 188, status: "Delivered" },
  { id: "MH-1043", buyer: "null_pointer", total: 129, status: "Processing" },
  { id: "MH-1044", buyer: "stack_overflow", total: 59, status: "Shipped" },
];

const tableBox =
  "mt-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60";
const th = "p-3 font-medium";

export default function VendorDashboard() {
  return (
    <main>
      <PageHeader tag="// vendor_console" title="Your store" />
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
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">Products</h2>
            <Link href="/vendor/products/new" className={btnGreen}>
              + Add product
            </Link>
          </div>
          <div className={tableBox}>
            <table className="font-code w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-slate-500">
                <tr>
                  <th className={th}>Name</th>
                  <th className={th}>Category</th>
                  <th className={th}>Price</th>
                  <th className={th}>Stock</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 5).map((p) => (
                  <tr key={p.id} className="border-b border-slate-800/60">
                    <td className="p-3 font-semibold text-white">{p.name}</td>
                    <td className="p-3">{p.category}</td>
                    <td className="p-3 text-cyan-400">{money(p.price)}</td>
                    <td className="p-3">{p.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">Recent orders</h2>
          <div className={tableBox}>
            <table className="font-code w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-slate-500">
                <tr>
                  <th className={th}>Order</th>
                  <th className={th}>Buyer</th>
                  <th className={th}>Total</th>
                  <th className={th}>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((o) => (
                  <tr key={o.id} className="border-b border-slate-800/60">
                    <td className="p-3 font-semibold text-white">{o.id}</td>
                    <td className="p-3">{o.buyer}</td>
                    <td className="p-3 text-cyan-400">{money(o.total)}</td>
                    <td className="p-3">
                      <Status status={o.status} />
                    </td>
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
