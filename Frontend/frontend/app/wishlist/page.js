import { PageHeader, ProductCard, wrap } from "@/components/ui";
import { products } from "@/lib/data";

export default function WishlistPage() {
  const saved = products.filter((p) => ["2", "4", "9"].includes(p.id));
  return (
    <main>
      <PageHeader tag="// wishlist" title="Saved gear">
        Items you saved for later.
      </PageHeader>
      <section
        className={`${wrap} grid gap-5 py-10 sm:grid-cols-2 lg:grid-cols-4`}
      >
        {saved.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </section>
    </main>
  );
}
