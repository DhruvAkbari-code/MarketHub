"use client";
import { useState } from "react";
import { inputClass } from "@/components/inputStyles";

export default function PasswordInput(props) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <input
        {...props}
        type={show ? "text" : "password"}
        className={inputClass}
      />
      <button
        type="button"
        onClick={() => setShow(!show)}
        className="font-code absolute right-4 top-1/2 -translate-y-1/2 text-xs font-semibold text-cyan-400"
      >
        {show ? "hide" : "show"}
      </button>
    </div>
  );
}
