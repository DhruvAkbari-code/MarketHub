import Link from "next/link";
import { Label, btnPrimary } from "@/components/ui";

export default function NotFound() {
  return (
    <main className="bg-grid flex min-h-[calc(100vh-73px)] items-center justify-center px-6">
      <div className="text-center">
        <div className="anim-float text-7xl">🔌</div>
        <Label className="mt-6 !text-cyan-400">// error</Label>
        <h1 className="font-code text-8xl font-bold text-white">404</h1>
        <p className="font-code mt-2 text-sm text-slate-400">page_not_found</p>
        <Link href="/" className={`${btnPrimary} mt-8`}>
          Back to home
        </Link>
      </div>
    </main>
  );
}
