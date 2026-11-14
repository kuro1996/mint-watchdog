import type { LeadStatus } from "@/lib/api";

const STYLES: Record<LeadStatus, string> = {
  NEW: "bg-sky-900 text-sky-200 border-sky-700",
  VERIFYING: "bg-amber-900 text-amber-200 border-amber-700",
  VERIFIED_FREE: "bg-emerald-900 text-emerald-200 border-emerald-700",
  PAID: "bg-slate-800 text-slate-300 border-slate-600",
  EXHAUSTED: "bg-slate-800 text-slate-400 border-slate-700",
  AVOID: "bg-red-900 text-red-200 border-red-700",
  UNVERIFIED: "bg-orange-900 text-orange-200 border-orange-700",
  STALE: "bg-zinc-800 text-zinc-300 border-zinc-600",
};

const LABELS: Record<LeadStatus, string> = {
  NEW: "NEW",
  VERIFYING: "VERIFYING",
  VERIFIED_FREE: "VERIFIED FREE",
  PAID: "PAID",
  EXHAUSTED: "EXHAUSTED",
  AVOID: "AVOID",
  UNVERIFIED: "UNVERIFIED",
  STALE: "STALE",
};

export default function StatusBadge({ status }: { status: LeadStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STYLES[status]}`}
    >
      {LABELS[status]}
    </span>
  );
}
