"use client";
import { useId } from "react";

const shapes = {
  laptop: (
    <>
      <rect x="20" y="22" width="60" height="42" rx="4" />
      <path d="M8 72h84l-7 9H15z" />
    </>
  ),
  keyboard: (
    <>
      <rect x="6" y="30" width="88" height="42" rx="7" />
      <path
        d="M20 42h6M34 42h6M48 42h6M62 42h6M76 42h6M26 52h6M40 52h6M54 52h6M68 52h6M30 62h40"
        fill="none"
      />
    </>
  ),
  mouse: (
    <>
      <rect x="30" y="12" width="40" height="76" rx="20" />
      <path d="M50 12v30M30 42h40" fill="none" />
    </>
  ),
  headphones: (
    <>
      <path d="M20 62V52a30 30 0 0 1 60 0v10" fill="none" />
      <rect x="12" y="56" width="18" height="30" rx="9" />
      <rect x="70" y="56" width="18" height="30" rx="9" />
    </>
  ),
  chip: (
    <>
      <path
        d="M38 18v10M50 18v10M62 18v10M38 72v10M50 72v10M62 72v10M18 38h10M18 50h10M18 62h10M72 38h10M72 50h10M72 62h10"
        fill="none"
      />
      <rect x="28" y="28" width="44" height="44" rx="5" />
      <rect x="42" y="42" width="16" height="16" rx="2" />
    </>
  ),
  rc: (
    <>
      <path d="M8 62v-10l14-4 10-16h30l10 16h20v14z" />
      <circle cx="28" cy="68" r="11" />
      <circle cx="74" cy="68" r="11" />
    </>
  ),
  stand: (
    <>
      <rect x="34" y="12" width="32" height="58" rx="5" />
      <path d="M24 88h52L64 70H36z" />
    </>
  ),
  phone: (
    <>
      <rect x="30" y="8" width="40" height="84" rx="8" />
      <path d="M43 17h14" fill="none" />
    </>
  ),
  screen: (
    <>
      <rect x="8" y="18" width="84" height="52" rx="4" />
      <path d="M50 70v14M32 86h36" fill="none" />
    </>
  ),
  spinner: (
    <>
      <circle cx="50" cy="26" r="15" />
      <circle cx="28" cy="64" r="15" />
      <circle cx="72" cy="64" r="15" />
      <circle cx="50" cy="52" r="11" />
    </>
  ),
};

export default function Sticker({ name = "chip", className = "h-24 w-24" }) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const sid = `s${uid}`;
  const gid = `g${uid}`;

  return (
    <svg
      viewBox="0 0 100 100"
      className={`holo ${className}`}
      overflow="visible"
      strokeLinejoin="round"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f9a8d4" />
          <stop offset="0.25" stopColor="#c4b5fd" />
          <stop offset="0.5" stopColor="#7dd3fc" />
          <stop offset="0.75" stopColor="#6ee7b7" />
          <stop offset="1" stopColor="#fde68a" />
        </linearGradient>
        <g id={sid}>{shapes[name] || shapes.chip}</g>
      </defs>
      {/* white sticker border, then holographic fill with black outline */}
      <use href={`#${sid}`} fill="#fff" stroke="#fff" strokeWidth="9" />
      <use
        href={`#${sid}`}
        fill={`url(#${gid})`}
        stroke="#111"
        strokeWidth="3"
      />
    </svg>
  );
}
