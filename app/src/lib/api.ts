/** Read-only client for the Week 1 Mint Watchdog API (server/api.py).
 * Only GET requests. No wallet, no signing, no transaction anywhere.
 * Base URL is configurable via NEXT_PUBLIC_API_URL (default
 * http://localhost:8000). A failed fetch is reported as STALE by callers —
 * it never means a mint is closed or exhausted. */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type LeadStatus =
  | "NEW"
  | "VERIFYING"
  | "VERIFIED_FREE"
  | "PAID"
  | "EXHAUSTED"
  | "AVOID"
  | "UNVERIFIED"
  | "STALE";

export interface Lead {
  id: number;
  contract: string;
  name: string | null;
  source: string | null;
  source_url: string | null;
  first_seen: string | null;
  status: LeadStatus;
  score_total: number | null;
  score_verdict: "PASS" | "AVOID" | "NEEDS HUMAN" | null;
  free_left: number | null;
  quota_left: number | null;
}

export interface Verification {
  checked_at: string | null;
  sourcify: string | null;
  total_supply: number | null;
  free_left: number | null;
  quota_left: number | null;
  mint_price: string | null;
  paused: boolean | null;
  owner: string | null;
  status: string | null;
}

export interface Score {
  scored_at: string | null;
  total: number;
  categories: {
    security: number;
    investor_protection: number;
    anti_manipulation: number;
    transparency: number;
    market_viability: number;
  };
  verdict: "PASS" | "AVOID" | "NEEDS HUMAN";
  hard_cap_applied: boolean;
  reasons: string[];
  missing: string[];
  /** Optional human note (demo fixtures only): flags an approximate total
   *  whose exact per-category split was not recorded. Never set on live data. */
  note?: string;
}

export interface LeadDetail extends Omit<Lead, "score_total" | "score_verdict"> {
  verification: Verification | null;
  score: Score | null;
}

export interface Holding {
  contract: string;
  token_id: string | null;
  name: string | null;
  locked: boolean | null;
  floor_note: string;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} -> HTTP ${res.status}`);
  return (await res.json()) as T;
}

export async function fetchHealth(): Promise<{ status: string; report_only: boolean }> {
  return getJson("/health");
}

export async function fetchLeads(): Promise<Lead[]> {
  const data = await getJson<{ leads: Lead[] }>("/leads");
  return data.leads;
}

export async function fetchLeadDetail(contract: string): Promise<LeadDetail | null> {
  try {
    return await getJson<LeadDetail>(`/leads/${contract}`);
  } catch {
    return null;
  }
}

export async function fetchHoldings(): Promise<Holding[]> {
  const data = await getJson<{ holdings: Holding[] }>("/holdings");
  return data.holdings;
}

/** Public BSC JSON-RPC endpoints (read-only). Tried in order; all failing
 *  means STALE, never "exhausted". */
export const BSC_RPC_ENDPOINTS = [
  "https://dataseed.bnbchain.org",
  "https://rpc.backrunshield.com",
  "https://dataseed1.ninicoin.io",
  "https://bsc-dataseed1.binance.org",
];

export async function rpcCall(method: string, params: unknown[]): Promise<unknown> {
  let lastError: unknown = null;
  for (const url of BSC_RPC_ENDPOINTS) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { result?: unknown; error?: { message: string } };
      if (data.error) throw new Error(data.error.message);
      return data.result;
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError instanceof Error ? lastError : new Error("all RPC endpoints failed");
}

export function isAddress(value: string): boolean {
  return /^0x[0-9a-fA-F]{40}$/.test(value.trim());
}
