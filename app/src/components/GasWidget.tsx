"use client";

import { useState } from "react";
import { isAddress, rpcCall } from "@/lib/api";

/** Gas widget — read-only. The user pastes an address; the widget reads
 * its BNB balance and the current gas price from public BSC RPC.
 * No transaction, no wallet connect, no signing, no private key.
 * Last-mint reference: Lumen Case 6 used 195,342 gas (receipt 0x1). */

const DEFAULT_THRESHOLD = "0.0001"; // BNB
const ESTIMATED_GAS = 200_000; // typical free mint, gas units

function weiToBnb(weiHex: string): number {
  return Number(BigInt(weiHex)) / 1e18;
}

function gweiToBnbPerGas(gasPriceGwei: number): number {
  return (gasPriceGwei * 1e9) / 1e18; // gwei -> wei per gas -> BNB per gas
}

export default function GasWidget() {
  const [address, setAddress] = useState(
    "0x921012ec43EC5d103E05117AdB7B0911d360F7B3",
  );
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [balance, setBalance] = useState<number | null>(null);
  const [gasPriceGwei, setGasPriceGwei] = useState<number | null>(null);
  const [checkedAt, setCheckedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function check() {
    if (!isAddress(address)) {
      setError("Not a valid BSC address (0x + 40 hex characters).");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [bal, price] = await Promise.all([
        rpcCall("eth_getBalance", [address.trim(), "latest"]),
        rpcCall("eth_gasPrice", []),
      ]);
      setBalance(weiToBnb(bal as string));
      setGasPriceGwei(Number(BigInt(price as string)) / 1e9);
      setCheckedAt(new Date().toLocaleTimeString());
    } catch {
      setError(
        "RPC read failed on every endpoint — data is STALE, not zero. Try again in a minute.",
      );
      setBalance(null);
      setGasPriceGwei(null);
    } finally {
      setLoading(false);
    }
  }

  const estimateBnb =
    gasPriceGwei === null ? null : gweiToBnbPerGas(gasPriceGwei) * ESTIMATED_GAS;
  const lowBalance =
    balance !== null && Number(threshold) > 0 && balance < Number(threshold);

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <h2 className="text-lg font-semibold">Gas widget — read-only</h2>
      <p className="mt-1 text-sm text-slate-400">
        Paste any BSC address to read its BNB balance. Nothing here can
        send a transaction.
      </p>
      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="0x…"
          spellCheck={false}
          className="min-w-0 flex-1 rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 font-mono text-sm"
          aria-label="BSC address to check"
        />
        <button
          onClick={check}
          disabled={loading}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold hover:bg-emerald-600 disabled:opacity-50"
        >
          {loading ? "Checking…" : "Check balance"}
        </button>
      </div>
      <label className="mt-3 block text-sm text-slate-400">
        Low-balance warning below (BNB)
        <input
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          inputMode="decimal"
          className="ml-2 w-32 rounded-lg border border-slate-600 bg-slate-800 px-2 py-1 font-mono text-sm"
        />
      </label>
      {error && (
        <p className="mt-3 rounded-lg border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-300">
          STALE — {error}
        </p>
      )}
      {balance !== null && (
        <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div>
            <dt className="text-slate-400">BNB balance</dt>
            <dd className="font-mono text-base font-semibold">
              {balance.toFixed(6)} BNB
            </dd>
          </div>
          <div>
            <dt className="text-slate-400">Gas price</dt>
            <dd className="font-mono text-base">
              {gasPriceGwei === null ? "—" : `${gasPriceGwei.toFixed(2)} gwei`}
            </dd>
          </div>
          <div>
            <dt className="text-slate-400">Est. mint cost ({ESTIMATED_GAS.toLocaleString()} gas)</dt>
            <dd className="font-mono text-base">
              {estimateBnb === null ? "—" : `${estimateBnb.toFixed(6)} BNB`}
            </dd>
          </div>
          <div>
            <dt className="text-slate-400">Last mint (Lumen Case 6)</dt>
            <dd className="font-mono text-base">195,342 gas</dd>
          </div>
        </dl>
      )}
      {lowBalance && (
        <p className="mt-3 rounded-lg border border-amber-700 bg-amber-900 px-3 py-2 text-sm font-semibold text-amber-200">
          Low balance: below your {threshold} BNB threshold. Top up gas
          yourself before any mint — this app never spends it.
        </p>
      )}
      {checkedAt && (
        <p className="mt-2 text-xs text-slate-500">
          Last checked {checkedAt} · BSC chain 56 · public RPC
        </p>
      )}
    </section>
  );
}
