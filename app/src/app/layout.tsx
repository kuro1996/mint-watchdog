import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mint Watchdog — free Agent ID mints on BSC",
  description:
    "Report-only dashboard: live free-mint leads, on-chain verification, 100-point rubric, holdings and gas. Never mints, never signs, never connects a wallet.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-800 bg-slate-950">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-4">
            <Link href="/" className="text-xl font-bold tracking-tight">
              Mint Watchdog
            </Link>
            <nav className="flex gap-5 text-sm font-medium">
              <Link href="/" className="text-slate-300 hover:text-white">
                Lead feed
              </Link>
              <Link href="/holdings" className="text-slate-300 hover:text-white">
                Holdings
              </Link>
            </nav>
            <span className="ml-auto rounded-full border border-emerald-700 bg-emerald-950 px-3 py-1 text-xs font-semibold text-emerald-300">
              REPORT-ONLY · no mint · no wallet · no signing
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
        <footer className="mx-auto max-w-5xl px-4 pb-8 text-xs text-slate-500">
          Mint Watchdog · Kiroween 2026 (Frankenstein) · BSC chain 56 ·
          Report-only: a PASS score is not a promise of profit, and &ldquo;no
          verified floor&rdquo; means exactly that — no price is invented.
          A win counts only on receipt 0x1 + token proven in the wallet.
        </footer>
      </body>
    </html>
  );
}
