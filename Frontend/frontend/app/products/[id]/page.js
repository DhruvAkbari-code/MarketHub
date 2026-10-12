import { notFound } from "next/navigation";
import AddToCart from "@/components/AddToCart";
import { Icon, Label, Pill, Bar, ProductCard, wrap } from "@/components/ui";
import { products, money } from "@/lib/data";

const distribution = [
  { stars: 5, value: 78 },
  { stars: 4, value: 15 },
  { stars: 3, value: 5 },
  { stars: 2, value: 1 },
  { stars: 1, value: 1 },
];

const reviews = [
  {
    name: "dev_aria",
    text: "Exactly as described. Fast shipping and great build quality.",
  },
  {
    name: "null_pointer",
    text: "Great value for the price. Would buy again from this vendor.",
  },
];

export default async function ProductPage({ params }) {
  const { id } = await params;
  const p = products.find((x) => x.id === id);
  if (!p) notFound();
  const related = products.filter((x) => x.id !== p.id).slice(0, 4);

  return (
    <main>
      <section className={`${wrap} grid gap-10 py-12 lg:grid-cols-2`}>
        {/* Image panel */}
        <div className="bg-grid group relative flex h-96 items-center justify-center overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60 lg:h-auto lg:min-h-[420px]">
          <div className="anim-float pointer-events-none absolute h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
          <Icon name={p.sticker} className="relative text-9xl" />
        </div>

        {/* Info */}
        <div>
          <div className="flex items-center gap-3">
            <Pill>{p.category}</Pill>
            <Label>by {p.vendor}</Label>
          </div>
          <h1 className="mt-4 text-4xl font-bold leading-tight tracking-tight text-white">
            {p.name}
          </h1>
          <p className="font-code mt-4 text-3xl font-bold text-cyan-400">
            {money(p.price)}
          </p>
          <Label className="mt-2">
            ★ {p.rating} / 5 · {p.stock} in stock
          </Label>

          <div className="mt-8 space-y-3 border-t border-slate-800 pt-6">
            <p className="font-code text-sm text-cyan-400">// specs</p>
            {p.specs.map((s) => (
              <p key={s} className="text-sm text-slate-300">
                <span className="text-emerald-400">✔</span> {s}
              </p>
            ))}
          </div>

          <AddToCart />
        </div>
      </section>

      {/* Reviews */}
      <section className="border-y border-slate-800 bg-slate-900/40 py-14">
        <div className={`${wrap} grid gap-10 md:grid-cols-2`}>
          <div>
            <p className="font-code text-sm text-cyan-400">
              // rating_distribution
            </p>
            <div className="mt-4 space-y-3">
              {distribution.map((d) => (
                <div key={d.stars} className="flex items-center gap-3">
                  <span className="font-code w-6 text-sm text-slate-300">
                    {d.stars}★
                  </span>
                  <div className="flex-1">
                    <Bar value={d.value} />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-4">
            <p className="font-code text-sm text-cyan-400">// reviews</p>
            {reviews.map((r) => (
              <div
                key={r.name}
                className="rounded-xl border border-slate-800 bg-slate-950/60 p-4"
              >
                <p className="font-code text-xs font-semibold text-slate-200">
                  {r.name} · ★★★★★
                </p>
                <p className="mt-2 text-sm text-slate-400">{r.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={`${wrap} py-14`}>
        <p className="font-code text-sm text-cyan-400">// related</p>
        <h2 className="mt-2 text-3xl font-bold text-white">
          You may also like
        </h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {related.map((r) => (
            <ProductCard key={r.id} product={r} />
          ))}
        </div>
      </section>
    </main>
  );
}
