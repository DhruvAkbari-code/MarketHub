import Link from "next/link";

const columns = [
  {
    title: "Shop",
    links: [
      ["All products", "/products"],
      ["Categories", "/#categories"],
      ["Wishlist", "/wishlist"],
      ["Cart", "/cart"],
    ],
  },
  {
    title: "Account",
    links: [
      ["Log in", "/login"],
      ["Sign up", "/register"],
      ["Orders", "/orders"],
      ["Profile", "/profile"],
    ],
  },
  {
    title: "Sell",
    links: [
      ["Become a vendor", "/become-vendor"],
      ["Vendor dashboard", "/vendor"],
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto grid max-w-6xl gap-10 px-6 py-14 md:grid-cols-4">
        <div>
          <Link
            href="/"
            className="font-code flex items-center gap-2 text-lg font-bold text-white"
          >
            <span className="text-cyan-400">&lt;/&gt;</span>
            market<span className="text-emerald-400">_</span>hub
          </Link>
          <p className="mt-4 text-sm leading-relaxed text-slate-500">
            Gear built for developers. Laptops, keyboards, circuits and
            everything on your desk.
          </p>
        </div>

        {columns.map((c) => (
          <div key={c.title}>
            <h4 className="font-code mb-4 text-sm font-semibold text-slate-200">
              {c.title}
            </h4>
            <ul className="space-y-3">
              {c.links.map(([label, href]) => (
                <li key={label}>
                  <Link
                    href={href}
                    className="text-sm text-slate-500 transition hover:text-cyan-400"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="font-code border-t border-slate-800 py-6 text-center text-xs text-slate-600">
        © {new Date().getFullYear()} market_hub — built by devs, for devs
      </div>
    </footer>
  );
}
