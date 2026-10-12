"use client";
import { useState } from "react";
import { btnPrimary, btnOutline } from "@/components/ui";

export default function AddToCart() {
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const [saved, setSaved] = useState(false);

  return (
    <div className="mt-8 flex items-center gap-3">
      <div className="font-code flex items-center rounded-lg border border-slate-700 text-white">
        <button
          onClick={() => setQty(Math.max(1, qty - 1))}
          className="px-4 py-3 hover:text-cyan-400"
        >
          −
        </button>
        <span className="w-10 text-center">{qty}</span>
        <button
          onClick={() => setQty(qty + 1)}
          className="px-4 py-3 hover:text-cyan-400"
        >
          +
        </button>
      </div>
      <button onClick={() => setAdded(true)} className={`${btnPrimary} flex-1`}>
        {added ? "Added ✓" : "Add to cart"}
      </button>
      <button
        onClick={() => setSaved(!saved)}
        className={btnOutline}
        aria-label="Save to wishlist"
      >
        {saved ? "♥" : "♡"}
      </button>
    </div>
  );
}
