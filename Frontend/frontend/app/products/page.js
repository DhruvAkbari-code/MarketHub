"use client";
import { useState } from "react";
import { PageHeader, ProductCard, Label, wrap } from "@/components/ui";
import { inputClass } from "@/components/inputStyles";
import { categories, products } from "@/lib/data";

export default function ProductsPage() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("All");
  const [sort, setSort] = useState("featured");

  let list = products.filter(
    (p) =>
      (cat === "All" || p.category === cat) &&
      p.name.toLowerCase().includes(q.toLowerCase()),
  );
  if (sort === "low") list = [...list].sort((a, b) => a.price - b.price);
  if (sort === "high") list = [...list].sort((a, b) => b.price - a.price);
  if (sort === "rating") list = [...list].sort((a, b) => b.rating - a.rating);

  return (
    <main>
      <PageHeader tag="// shop" title="All gear">
        Search, filter and sort everything on the marketplace.
      </PageHeader>

      <section className={`${wrap} py-10`}>
        <div className="flex flex-col gap-3 md:flex-row">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="> search products..."
            className={`${inputClass} font-code md:flex-1`}
          />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className={`${inputClass} md:w-56`}
          >
            <option value="featured">Sort: Featured</option>
            <option value="low">Price: Low to high</option>
            <option value="high">Price: High to low</option>
            <option value="rating">Top rated</option>
          </select>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {["All", ...categories.map((c) => c.name)].map((name) => (
            <button
              key={name}
              onClick={() => setCat(name)}
              className={`font-code rounded-full border px-4 py-1.5 text-xs transition ${
                cat === name
                  ? "border-cyan-400 bg-cyan-400 text-slate-950"
                  : "border-slate-700 text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
              }`}
            >
              {name}
            </button>
          ))}
        </div>

        <Label className="mt-8">{list.length} results</Label>
        {list.length === 0 ? (
          <p className="font-code mt-6 text-sm text-slate-400">
            No products found. Try another search.
          </p>
        ) : (
          <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {list.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
