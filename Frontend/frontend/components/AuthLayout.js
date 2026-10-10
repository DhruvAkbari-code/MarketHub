import GuestGuard from "@/components/GuestGuard";

const panels = {
  login: {
    tag: "// welcome_back",
    heading: "Your setup is waiting.",
    text: "Log in to track your orders, save your favorite gear and pick up right where you left off.",
    emojis: ["💻", "🎧"],
    blob: "bg-cyan-500/20",
    ring: "border-cyan-400/20",
    tagColor: "text-cyan-400",
    lines: [
      { text: "$ markethub login", color: "text-slate-300" },
      { text: "✔ secure connection", color: "text-emerald-400" },
      { text: "✔ loading your wishlist", color: "text-emerald-400" },
      { text: "→ welcome back, dev", color: "text-cyan-400" },
    ],
    points: [],
  },
  register: {
    tag: "// join_the_hub",
    heading: "Build the setup you've always wanted.",
    text: "Create a free account and get access to keyboards, laptops, circuits and everything a developer loves.",
    emojis: ["⌨️", "🖱️"],
    blob: "bg-violet-500/20",
    ring: "border-violet-400/20",
    tagColor: "text-violet-400",
    lines: [
      { text: "$ markethub register", color: "text-slate-300" },
      { text: "→ creating your account...", color: "text-cyan-400" },
      { text: "✔ welcome to market_hub", color: "text-emerald-400" },
    ],
    points: [
      "Save your favorite gear",
      "Track every order",
      "Get notified on new drops",
    ],
  },
  vendor: {
    tag: "// for_sellers",
    heading: "Turn your gear into a store.",
    text: "Sell straight to thousands of developers. Tell us about your store and we'll take it from there.",
    emojis: ["🔌", "🏎️"],
    blob: "bg-emerald-500/20",
    ring: "border-emerald-400/20",
    tagColor: "text-emerald-400",
    lines: [
      { text: "$ markethub vendor --apply", color: "text-slate-300" },
      { text: "✔ store details received", color: "text-emerald-400" },
      { text: "→ ready to start selling", color: "text-cyan-400" },
    ],
    points: [
      "List products in minutes",
      "Reach developers worldwide",
      "Manage your own store",
    ],
  },
  forgot: {
    tag: "// recover_access",
    heading: "Locked out? No problem.",
    text: "Enter your email and we'll send you a link to reset your password.",
    emojis: ["📱", "🔌"],
    blob: "bg-sky-500/20",
    ring: "border-sky-400/20",
    tagColor: "text-sky-400",
    lines: [
      { text: "$ markethub reset-password", color: "text-slate-300" },
      { text: "→ sending reset link...", color: "text-cyan-400" },
      { text: "✔ check your inbox", color: "text-emerald-400" },
    ],
    points: [],
  },
};

export default function AuthLayout({
  variant = "login",
  title,
  subtitle,
  wide = false,
  children,
}) {
  const panel = panels[variant];

  return (
    <main className="flex min-h-[calc(100vh-73px)]">
      <GuestGuard />

      {/* Left side: animations and text */}
      <section className="bg-grid relative hidden flex-1 items-center justify-center overflow-hidden border-r border-slate-800 p-12 lg:flex">
        <div
          className={`anim-float pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full blur-3xl ${panel.blob}`}
        />
        <div
          className={`anim-float pointer-events-none absolute -bottom-24 -right-24 h-80 w-80 rounded-full blur-3xl ${panel.blob}`}
          style={{ animationDelay: "2s" }}
        />
        <div
          className={`pointer-events-none absolute h-[520px] w-[520px] animate-spin rounded-full border border-dashed ${panel.ring}`}
          style={{ animationDuration: "40s" }}
        />

        <div className="relative z-10 w-full max-w-md">
          <p className={`font-code text-sm ${panel.tagColor}`}>{panel.tag}</p>
          <h2 className="mt-3 text-4xl font-bold leading-tight text-white">
            {panel.heading}
          </h2>
          <p className="mt-4 text-slate-400">{panel.text}</p>

          {panel.points.length > 0 && (
            <ul className="mt-6 space-y-2">
              {panel.points.map((point) => (
                <li
                  key={point}
                  className="flex items-center gap-2 text-sm text-slate-300"
                >
                  <span className="text-emerald-400">✔</span> {point}
                </li>
              ))}
            </ul>
          )}

          <div className="relative mt-10">
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
                {panel.lines.map((line, i) => (
                  <p
                    key={line.text}
                    className={`${line.color} anim-fade-up`}
                    style={{ animationDelay: `${0.3 + i * 0.7}s` }}
                  >
                    {line.text}
                    {i === panel.lines.length - 1 && (
                      <span className="anim-blink ml-1">▍</span>
                    )}
                  </p>
                ))}
              </div>
            </div>
            <span className="anim-float absolute -right-5 -top-8 text-5xl">
              {panel.emojis[0]}
            </span>
            <span
              className="anim-float absolute -bottom-8 -left-5 text-5xl"
              style={{ animationDelay: "1.5s" }}
            >
              {panel.emojis[1]}
            </span>
          </div>
        </div>
      </section>

      {/* Right side: form */}
      <section className="flex flex-1 items-center justify-center bg-[#0b0f19] px-6 py-12">
        <div
          className={`anim-fade-up w-full ${wide ? "max-w-lg" : "max-w-md"}`}
        >
          <h1 className="font-code text-2xl font-bold text-white">{title}</h1>
          <p className="mt-2 text-sm text-slate-400">{subtitle}</p>
          <div className="mt-8">{children}</div>
        </div>
      </section>
    </main>
  );
}
