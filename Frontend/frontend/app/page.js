import Link from "next/link";
import Typewriter from "@/components/Typewriter";
import { Icon, Label, ProductCard, btnGreen, wrap } from "@/components/ui";
import { categories, products } from "@/lib/data";

const terminalLines = [
  { text: '$ markethub search "mechanical keyboard"', color: "text-slate-300" },
  { text: "✔ 128 items found", color: "text-emerald-400" },
  { text: "✔ 42 verified vendors", color: "text-emerald-400" },
  { text: "$ markethub ship --fast", color: "text-slate-300" },
  { text: "→ delivering to your desk...", color: "text-cyan-400" },
];

const steps = [
  {
    cmd: "register",
    title: "Create your account",
    text: "Sign up with your email or Google in seconds.",
  },
  {
    cmd: "browse",
    title: "Find your gear",
    text: "Search by category, brand or vendor and compare specs.",
  },
  {
    cmd: "deploy",
    title: "Get it delivered",
    text: "Order securely and track it all the way to your desk.",
  },
];

const features = [
  {
    icon: "🧪",
    title: "Real specs",
    text: "Listings show the details devs actually care about.",
  },
  {
    icon: "✅",
    title: "Verified vendors",
    text: "Every vendor is reviewed before they can sell.",
  },
  {
    icon: "🔒",
    title: "Secure checkout",
    text: "Your payment is protected on every order.",
  },
  {
    icon: "🚀",
    title: "Fast shipping",
    text: "Quick, trackable delivery on all orders.",
  },
];

const perks = [
  "List products in minutes",
  "Reach thousands of developers",
  "Manage your own store",
];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="bg-grid relative overflow-hidden">
        <div className="anim-float pointer-events-none absolute -top-32 left-1/4 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
        <div
          className="anim-float pointer-events-none absolute right-0 top-40 h-96 w-96 rounded-full bg-violet-500/20 blur-3xl"
          style={{ animationDelay: "2s" }}
        />

        <div className="relative mx-auto grid max-w-6xl items-center gap-14 px-6 py-24 lg:grid-cols-2">
          <div>
            <span className="font-code inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-1.5 text-xs text-emerald-300">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              new drops every week
            </span>

            <h1 className="mt-6 text-5xl font-bold leading-tight tracking-tight text-white md:text-6xl">
              Gear up for your next{" "}
              <span className="block min-h-[1.2em]">
                <Typewriter
                  words={[
                    "laptop.",
                    "keyboard.",
                    "headphones.",
                    "circuit.",
                    "setup.",
                  ]}
                />
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-lg text-slate-400">
              Market Hub is the marketplace made for developers. Everything a
              techie loves, from one place.
            </p>

            <div className="mt-8 flex max-w-lg items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/80 p-2">
              <span className="font-code pl-3 text-cyan-400">&gt;</span>
              <input
                type="text"
                placeholder="search mechanical keyboard..."
                className="font-code flex-1 bg-transparent px-2 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-500"
              />
              <Link
                href="/products"
                className="rounded-lg bg-cyan-400 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
              >
                Search
              </Link>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href="/products"
                className="rounded-lg border border-slate-700 px-5 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-400"
              >
                Shop now
              </Link>
              <Link
                href="/become-vendor"
                className="rounded-lg border border-emerald-400/40 px-5 py-2.5 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-400/10"
              >
                Become a vendor
              </Link>
            </div>
          </div>

          {/* Terminal */}
          <div className="relative">
            <div className="anim-glow rounded-2xl border border-slate-700 bg-slate-900/80 backdrop-blur">
              <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-3">
                <span className="h-3 w-3 rounded-full bg-rose-400" />
                <span className="h-3 w-3 rounded-full bg-amber-400" />
                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                <span className="font-code ml-3 text-xs text-slate-500">
                  ~/market-hub
                </span>
              </div>
              <div className="font-code space-y-3 p-6 text-sm">
                {terminalLines.map((line, i) => (
                  <p
                    key={line.text}
                    className={`${line.color} anim-fade-up`}
                    style={{ animationDelay: `${0.4 + i * 0.7}s` }}
                  >
                    {line.text}
                    {i === terminalLines.length - 1 && (
                      <span className="anim-blink ml-1">▍</span>
                    )}
                  </p>
                ))}
              </div>
            </div>
            <span className="anim-float absolute -right-4 -top-8 text-5xl">
              🎧
            </span>
            <span
              className="anim-float absolute -bottom-8 -left-4 text-5xl"
              style={{ animationDelay: "1.5s" }}
            >
              ⌨️
            </span>
          </div>
        </div>
      </section>

      {/* Ticker */}
      <section className="overflow-hidden border-y border-slate-800 bg-slate-900/50 py-4">
        <div className="anim-marquee font-code flex text-sm text-slate-400">
          {[...categories, ...categories].map((c, i) => (
            <span key={i} className="whitespace-nowrap px-6">
              <Icon name={c.sticker} className="text-base" /> {c.name}
            </span>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section id="categories" className={`${wrap} py-24`}>
        <div className="text-center">
          <p className="font-code text-sm text-cyan-400">// categories</p>
          <h2 className="mt-2 text-3xl font-bold text-white">
            Everything on your desk
          </h2>
          <p className="mt-3 text-slate-400">
            Pick a category and start exploring.
          </p>
        </div>
        <div className="mt-12 grid grid-cols-2 gap-5 md:grid-cols-3 lg:grid-cols-5">
          {categories.map((c) => (
            <Link
              key={c.name}
              href="/products"
              className="card group p-6 text-center"
            >
              <Icon name={c.sticker} className="text-4xl" />
              <p className="mt-3 text-sm font-semibold text-slate-200">
                {c.name}
              </p>
              <p className="font-code mt-1 text-xs text-slate-600 transition group-hover:text-cyan-400">
                ls /{c.name.toLowerCase().replace(" ", "-")}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured */}
      <section className="border-y border-slate-800 bg-slate-900/40 py-24">
        <div className={wrap}>
          <div className="flex items-end justify-between">
            <div>
              <p className="font-code text-sm text-cyan-400">// featured</p>
              <h2 className="mt-2 text-3xl font-bold text-white">New drops</h2>
            </div>
            <Link
              href="/products"
              className="font-code text-sm text-cyan-400 hover:underline"
            >
              view all →
            </Link>
          </div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {products.slice(0, 4).map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className={`${wrap} py-24`}>
        <div className="text-center">
          <p className="font-code text-sm text-cyan-400">// how_it_works</p>
          <h2 className="mt-2 text-3xl font-bold text-white">
            Three commands to your setup
          </h2>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {steps.map((s, i) => (
            <div
              key={s.title}
              className="rounded-xl border border-slate-800 bg-slate-950/60 p-8 transition hover:border-emerald-400/40"
            >
              <p className="font-code text-sm text-emerald-400">
                0{i + 1} / {s.cmd}()
              </p>
              <h3 className="mt-4 text-lg font-semibold text-white">
                {s.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {s.text}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section
        id="features"
        className="border-t border-slate-800 bg-slate-900/40 py-24"
      >
        <div className={wrap}>
          <div className="text-center">
            <p className="font-code text-sm text-cyan-400">// why_us</p>
            <h2 className="mt-2 text-3xl font-bold text-white">
              Built for developers
            </h2>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div key={f.title} className="card p-6">
                <div className="text-3xl">{f.icon}</div>
                <h3 className="mt-4 font-semibold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{f.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Become a vendor */}
      <section id="sell" className="px-6 py-24">
        <div className="mx-auto grid max-w-5xl items-center gap-10 overflow-hidden rounded-3xl border border-emerald-400/20 bg-gradient-to-br from-emerald-400/10 via-slate-900 to-cyan-400/10 p-10 md:grid-cols-2 md:p-14">
          <div>
            <p className="font-code text-sm text-emerald-400">// for_sellers</p>
            <h2 className="mt-2 text-3xl font-bold text-white">
              Got gear to sell?
            </h2>
            <p className="mt-3 text-slate-400">
              Become a Market Hub vendor and sell straight to developers.
            </p>
            <ul className="mt-6 space-y-2">
              {perks.map((perk) => (
                <li
                  key={perk}
                  className="flex items-center gap-2 text-sm text-slate-300"
                >
                  <span className="text-emerald-400">✔</span> {perk}
                </li>
              ))}
            </ul>
            <Link href="/become-vendor" className={`${btnGreen} mt-8`}>
              Become a vendor
            </Link>
          </div>
          <pre className="font-code overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/80 p-5 text-sm leading-relaxed text-slate-300">
            {`const vendor = {
  store: "your_store",
  sells: ["keyboards", "mice"],
  status: "ready to ship",
};`}
          </pre>
        </div>
      </section>
    </main>
  );
}
