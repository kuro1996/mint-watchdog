"use client";

import { useEffect, useState } from "react";
import GasWidget from "@/components/GasWidget";
import { fetchHoldings, type Holding } from "@/lib/api";
import { DEMO_HOLDINGS } from "@/lib/demo";

export default function HoldingsPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [stale, setStale] = useState(false);
  const [lastChecked, setLastChecked] = useState<string | null>(null);

  useEffect(() => {
    fetchHoldings()
      .then((data) => {
        setHoldings(data);
        setStale(false);
      })
      .catch(() => setStale(true))
      .finally(() => setLastChecked(new Date().toLocaleTimeString()));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Holdings</h1>
        <p className="mt-1 text-sm text-slate-400">
          NFTs and tokens already held from free mints, with lock status.
          Where no price is verified, this page says{" "}
          <strong>no verified floor</strong> — never an invented number.
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Live holdings last checked: {lastChecked ?? "—"}
          {stale &&
            " · STALE — API unreachable, showing demo examples only."}
        </p>
      </div>

      {holdings.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold">Live holdings (from API)</h2>
          <ul className="mt-3 space-y-3">
            {holdings.map((h) => (
              <li
                key={`${h.contract}-${h.token_id ?? "token"}`}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
              >
                <p className="font-semibold">
                  {h.name ?? h.contract}
                  {h.token_id ? ` #${h.token_id}` : ""}
                </p>
                <p className="mt-1 font-mono text-xs text-slate-400">
                  {h.contract}
                </p>
                <p className="mt-1 text-sm text-slate-400">
                  {h.locked === null
                    ? "Lock status unknown"
                    : h.locked
                      ? "Locked"
                      : "Transferable"}{" "}
                  · Floor: {h.floor_note}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold">
          Demo examples — verified wallet contents, 2026-11-13/14
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          Real holdings of the example wallet (Agent ID kuro1999.ai).
          Labelled as examples; not live API data.
        </p>
        <ul className="mt-3 space-y-3">
          {DEMO_HOLDINGS.map((h) => (
            <li
              key={`${h.contract}-${h.token_id ?? "token"}`}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
            >
              <div className="flex flex-wrap items-center gap-3">
                <p className="font-semibold">{h.name}</p>
                <span className="rounded-full border border-sky-700 bg-sky-950 px-2.5 py-0.5 text-xs font-semibold text-sky-200">
                  DEMO EXAMPLE
                </span>
              </div>
              <p className="mt-1 font-mono text-xs text-slate-400">
                {h.contract}
              </p>
              <p className="mt-1 text-sm text-slate-400">
                {h.lockNote} · Floor: {h.floor_note}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <GasWidget />
    </div>
  );
}
