import Link from "next/link";

const links = [
  { label: "Shop", href: "/products" },
  { label: "Categories", href: "/#categories" },
  { label: "Wishlist", href: "/wishlist" },
  { label: "Orders", href: "/orders" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-[#0b0f19]/80 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="font-code flex items-center gap-2 text-lg font-bold text-white"
        >
          <span className="text-cyan-400">&lt;/&gt;</span>
          market<span className="text-emerald-400">_</span>hub
        </Link>

        <ul className="hidden items-center gap-8 lg:flex">
          {links.map((l) => (
            <li key={l.label}>
              <Link
                href={l.href}
                className="text-sm font-medium text-slate-400 transition hover:text-cyan-400"
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-3">
          <Link
            href="/cart"
            className="text-sm font-semibold text-slate-300 transition hover:text-cyan-400"
          >
            🛒 Cart (2)
          </Link>
          <Link
            href="/login"
            className="hidden px-3 py-2 text-sm font-semibold text-slate-300 transition hover:text-cyan-400 sm:block"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="hidden rounded-lg bg-cyan-400 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 sm:block"
          >
            Sign up
          </Link>

          <details className="relative lg:hidden">
            <summary className="font-code cursor-pointer list-none rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300">
              Menu
            </summary>
            <ul className="absolute right-0 mt-2 w-48 space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4 text-sm text-slate-300">
              {links.map((l) => (
                <li key={l.label}>
                  <Link href={l.href}>{l.label}</Link>
                </li>
              ))}
              <li>
                <Link href="/login">Log in</Link>
              </li>
              <li>
                <Link href="/register">Sign up</Link>
              </li>
            </ul>
          </details>
        </div>
      </nav>
    </header>
  );
}
