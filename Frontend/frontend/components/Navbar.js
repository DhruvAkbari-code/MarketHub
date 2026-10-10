"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

// visible to everyone
const publicLinks = [
  { label: "Shop", href: "/products" },
  { label: "Categories", href: "/#categories" },
];

// visible only when logged in
const userLinks = [{ label: "Wishlist", href: "/wishlist" }];

function Avatar({ user }) {
  if (user.profile_picture) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={user.profile_picture}
        alt={user.username}
        referrerPolicy="no-referrer"
        className="h-9 w-9 rounded-full border border-cyan-400/50 object-cover"
      />
    );
  }
  return (
    <span className="font-code flex h-9 w-9 items-center justify-center rounded-full border border-cyan-400/50 bg-cyan-400/10 text-sm font-bold text-cyan-300">
      {user.username?.[0]?.toUpperCase() || "?"}
    </span>
  );
}

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setUser(null);
        setReady(true);
        return;
      }
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`,
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );
        if (res.ok) {
          setUser(await res.json());
        } else {
          localStorage.removeItem("access_token");
          setUser(null);
        }
      } catch (err) {
        // server unreachable: keep the current state
      }
      setReady(true);
    }

    loadUser();
    window.addEventListener("auth-change", loadUser);
    return () => window.removeEventListener("auth-change", loadUser);
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    setUser(null);
    setOpen(false);
    window.dispatchEvent(new Event("auth-change"));
    router.replace("/");
  }

  const links = user ? [...publicLinks, ...userLinks] : publicLinks;

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
          {ready && user && (
            <Link
              href="/cart"
              className="text-sm font-semibold text-slate-300 transition hover:text-cyan-400"
            >
              🛒 Cart (2)
            </Link>
          )}

          {ready && !user && (
            <>
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
            </>
          )}

          {ready && user && (
            <div className="relative">
              <button
                onClick={() => setOpen(!open)}
                aria-label="Account menu"
                className="block rounded-full"
              >
                <Avatar user={user} />
              </button>

              {open && (
                <div className="absolute right-0 mt-3 w-56 rounded-xl border border-slate-700 bg-slate-900 p-2 shadow-xl">
                  <div className="border-b border-slate-800 px-3 py-2">
                    <p className="truncate text-sm font-semibold text-white">
                      {user.username}
                    </p>
                    <p className="font-code truncate text-xs text-slate-500">
                      {user.email}
                    </p>
                  </div>
                  <Link
                    href="/profile"
                    onClick={() => setOpen(false)}
                    className="mt-1 block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
                  >
                    Profile
                  </Link>
                  <Link
                    href="/orders"
                    onClick={() => setOpen(false)}
                    className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
                  >
                    My orders
                  </Link>
                  <button
                    onClick={logout}
                    className="block w-full rounded-lg px-3 py-2 text-left text-sm text-rose-400 hover:bg-slate-800"
                  >
                    Log out
                  </button>
                </div>
              )}
            </div>
          )}

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
              {ready && !user && (
                <>
                  <li>
                    <Link href="/login">Log in</Link>
                  </li>
                  <li>
                    <Link href="/register">Sign up</Link>
                  </li>
                </>
              )}
            </ul>
          </details>
        </div>
      </nav>
    </header>
  );
}
