"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import GasWidget from "@/components/GasWidget";
import StatusBadge from "@/components/StatusBadge";
import { fetchLeads, type Lead } from "@/lib/api";
import { DEMO_CANDIDATES } from "@/lib/demo";

const POLL_MS = 60_000;

/** A lead is alert-worthy only when the chain confirms it: VERIFIED FREE
 *  + rubric PASS + free supply left + quota left. */
function isAlertWorthy(lead: Lead): boolean {
  return (
    lead.status === "VERIFIED_FREE" &&
    lead.score_verdict === "PASS" &&
    (lead.free_left ?? 0) > 0 &&
    (lead.quota_left ?? 0) > 0
  );
}

export default function FeedPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stale, setStale] = useState(false);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await fetchLeads();
      setLeads(data);
      setStale(false);
    } catch {
      // Failed read = STALE. Never conclude EXHAUSTED from a failed read.
      setStale(true);
    } finally {
      setLastChecked(new Date().toLocaleTimeString());
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

  const alerts = leads.filter(isAlertWorthy);
  // Demo examples are NEVER counted as open windows: their windows
  // closed on 2026-11-13/14 (Lumen Case 6 ended 01:00 WIB 2026-11-14).
  // They are shown in a separate, clearly labelled box below.
  const demoAlerts = DEMO_CANDIDATES.filter(
    (c) => c.status === "VERIFIED_FREE" && c.score?.verdict === "PASS",
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Live lead feed</h1>
        <p className="mt-1 text-sm text-slate-400">
          Free-mint candidates from public X and Telegram pages, newest
          first. Each one is verified on-chain before it is shown as free.
        </p>
        <p className="mt-1 text-xs text-slate-500">
          API polls every 60 s · Last checked: {lastChecked ?? "—"}
          {stale && (
            <span className="ml-2 font-semibold text-zinc-300">
              · STALE — API unreachable, showing last good data (never
              treated as exhausted)
            </span>
          )}
        </p>
      </div>

      {stale && (
        <div className="rounded-xl border border-zinc-600 bg-zinc-800 px-4 py-3 text-sm font-semibold text-zinc-200">
          STALE — the read-only API is unreachable. Data below may be old;
          nothing here means a mint is closed or exhausted.
        </div>
      )}

      {alerts.length > 0 && (
        <div
          role="alert"
          className="rounded-xl border border-emerald-600 bg-emerald-950 px-4 py-3"
        >
          <p className="text-sm font-bold text-emerald-300">
            Verified-free window open — {alerts.length} live candidate
            {alerts.length > 1 ? "s" : ""}:
          </p>
          <ul className="mt-2 space-y-1 text-sm text-emerald-100">
            {alerts.map((lead) => (
              <li key={lead.contract}>
                <Link
                  href={`/candidate/${lead.contract}`}
                  className="underline"
                >
                  {lead.name ?? lead.contract}
                </Link>{" "}
                — score {lead.score_total}/100, free left{" "}
                {lead.free_left ?? "?"}, quota left {lead.quota_left ?? "?"}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-emerald-200/80">
            Report-only: this dashboard cannot mint for you. Copy the
            contract from the candidate page and mint from your own wallet
            after your own check.
          </p>
        </div>
      )}

      {demoAlerts.length > 0 && (
        <div className="rounded-xl border border-slate-600 bg-slate-900 px-4 py-3">
          <p className="text-sm font-bold text-slate-200">
            Demo examples — windows now closed (real past mints, not live
            leads):
          </p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {demoAlerts.map((c) => (
              <li key={c.contract}>
                <Link href={`/candidate/${c.contract}`} className="underline">
                  {c.name}
                </Link>{" "}
                — score {c.score?.total}/100 (see candidate page for the
                receipt lesson)
              </li>
            ))}
          </ul>
        </div>
      )}

      <section>
        <h2 className="text-lg font-semibold">Live leads</h2>
        {loading ? (
          <p className="mt-2 text-sm text-slate-400">Loading…</p>
        ) : leads.length === 0 ? (
          <p className="mt-2 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-400">
            No live leads yet — the watcher has not stored any candidate.
            Demo examples below show what a verified candidate looks like.
          </p>
        ) : (
          <ul className="mt-3 space-y-3">
            {leads.map((lead) => (
              <li
                key={lead.contract}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <Link
                    href={`/candidate/${lead.contract}`}
                    className="font-semibold underline"
                  >
                    {lead.name ?? lead.contract}
                  </Link>
                  <StatusBadge status={lead.status} />
                  {lead.score_verdict && (
                    <span className="text-sm text-slate-300">
                      Score {lead.score_total ?? "—"}/100 ·{" "}
                      {lead.score_verdict}
                    </span>
                  )}
                </div>
                <p className="mt-1 font-mono text-xs text-slate-400">
                  {lead.contract}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Source: {lead.source ?? "unknown"}
                  {lead.first_seen ? ` · first seen ${lead.first_seen}` : ""}
                  {lead.free_left !== null &&
                    ` · free left ${lead.free_left}`}
                  {lead.quota_left !== null &&
                    ` · quota left ${lead.quota_left}`}
                  {lead.source_url && (
                    <>
                      {" · "}
                      <a
                        href={lead.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="underline"
                      >
                        original post
                      </a>
                    </>
                  )}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold">
          Demo examples — real mints, clearly labelled
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          These three really happened (receipt 0x1 + token in wallet,
          2026-11-13/14). They are examples, not live leads — their
          windows are now closed.
        </p>
        <ul className="mt-3 space-y-3">
          {DEMO_CANDIDATES.map((c) => (
            <li
              key={c.contract}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
            >
              <div className="flex flex-wrap items-center gap-3">
                <Link
                  href={`/candidate/${c.contract}`}
                  className="font-semibold underline"
                >
                  {c.name}
                </Link>
                <StatusBadge status={c.status} />
                <span className="rounded-full border border-sky-700 bg-sky-950 px-2.5 py-0.5 text-xs font-semibold text-sky-200">
                  DEMO EXAMPLE
                </span>
                <span className="text-sm text-slate-300">
                  Score {c.score?.total}/100 · {c.score?.verdict}
                </span>
              </div>
              <p className="mt-1 font-mono text-xs text-slate-400">
                {c.contract}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Source: {c.source} · first seen {c.first_seen} ·{" "}
                {c.name?.includes("TEGONG")
                  ? "+10,000,000 MIAO, locked until sellout"
                  : c.name?.includes("Zeroday")
                    ? "preview #167 vs actual #169"
                    : "preview #1500 = actual #1500"}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <GasWidget />
    </div>
  );
}
