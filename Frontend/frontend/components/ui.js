import Link from "next/link";
import { money } from "@/lib/data";

export const wrap = "mx-auto max-w-6xl px-6";

export const btnPrimary =
  "inline-block rounded-lg bg-cyan-400 px-6 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-60";
export const btnGreen =
  "inline-block rounded-lg bg-emerald-400 px-6 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-emerald-300";
export const btnOutline =
  "inline-block rounded-lg border border-slate-700 px-6 py-3 text-center text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-400";

const icons = {
  laptop: "💻",
  keyboard: "⌨️",
  mouse: "🖱️",
  headphones: "🎧",
  chip: "🔌",
  rc: "🏎️",
  stand: "📲",
  phone: "📱",
  screen: "🖥️",
  spinner: "🌀",
};

export function Icon({ name, className = "text-4xl" }) {
  return (
    <span
      className={`inline-block transition group-hover:-rotate-6 group-hover:scale-125 ${className}`}
    >
      {icons[name] || "🔌"}
    </span>
  );
}

export function Label({ children, className = "" }) {
  return (
    <p className={`font-code text-xs text-slate-500 ${className}`}>
      {children}
    </p>
  );
}

const statusColors = {
  Delivered: "border-emerald-400/40 bg-emerald-400/10 text-emerald-300",
  Approved: "border-emerald-400/40 bg-emerald-400/10 text-emerald-300",
  Shipped: "border-cyan-400/40 bg-cyan-400/10 text-cyan-300",
  Processing: "border-amber-400/40 bg-amber-400/10 text-amber-300",
  Pending: "border-amber-400/40 bg-amber-400/10 text-amber-300",
  Rejected: "border-rose-400/40 bg-rose-400/10 text-rose-300",
};

export function Status({ status }) {
  return (
    <span
      className={`font-code inline-block rounded-full border px-3 py-0.5 text-xs ${statusColors[status] || statusColors.Shipped}`}
    >
      {status}
    </span>
  );
}

export function Pill({ children }) {
  return (
    <span className="font-code inline-block rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300">
      {children}
    </span>
  );
}

export function Bar({ value }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
      <div
        className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

export function PageHeader({ tag, title, children }) {
  return (
    <div className="bg-grid border-b border-slate-800">
      <div className={`${wrap} py-12`}>
        <p className="font-code text-sm text-cyan-400">{tag}</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-white md:text-5xl">
          {title}
        </h1>
        {children && <p className="mt-3 max-w-xl text-slate-400">{children}</p>}
      </div>
    </div>
  );
}

export function Or() {
  return (
    <div className="my-6 flex items-center gap-4">
      <div className="h-px flex-1 bg-slate-800" />
      <span className="font-code text-xs uppercase text-slate-500">or</span>
      <div className="h-px flex-1 bg-slate-800" />
    </div>
  );
}

export function ProductCard({ product: p }) {
  return (
    <Link href={`/product/${p.id}`} className="card group block p-5">
      <div className="flex justify-between">
        <Label>{p.category}</Label>
        <Label>★ {p.rating}</Label>
      </div>
      <div className="my-4 flex h-36 items-center justify-center rounded-lg bg-slate-950/60">
        <Icon name={p.sticker} className="text-6xl" />
      </div>
      <h3 className="font-semibold text-white">{p.name}</h3>
      <div className="mt-3 flex items-end justify-between">
        <p className="font-code text-lg font-bold text-cyan-400">
          {money(p.price)}
        </p>
        <Label>by {p.vendor}</Label>
      </div>
    </Link>
  );
}
