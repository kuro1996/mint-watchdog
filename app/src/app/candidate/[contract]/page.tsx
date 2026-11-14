import Link from "next/link";
import StatusBadge from "@/components/StatusBadge";
import { fetchLeadDetail, isAddress, type LeadDetail } from "@/lib/api";
import { findDemoCandidate } from "@/lib/demo";

const CATEGORY_LABELS: { key: keyof NonNullable<LeadDetail["score"]>["categories"]; label: string; max: number }[] = [
  { key: "security", label: "Security", max: 30 },
  { key: "investor_protection", label: "Investor Protection", max: 25 },
  { key: "anti_manipulation", label: "Anti-Manipulation", max: 20 },
  { key: "transparency", label: "Transparency", max: 15 },
  { key: "market_viability", label: "Market Viability", max: 10 },
];

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-800 py-2 text-sm last:border-0">
      <span className="text-slate-400">{label}</span>
      <span className="font-mono text-right">{value}</span>
    </div>
  );
}

export default async function CandidatePage({
  params,
}: {
  params: Promise<{ contract: string }>;
}) {
  const { contract } = await params;
  const demo = findDemoCandidate(contract);
  const live = isAddress(contract) ? await fetchLeadDetail(contract) : null;
  const detail: LeadDetail | null = live ?? demo ?? null;
  const isDemo = !live && !!demo;

  if (!detail) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Candidate not found</h1>
        <p className="text-sm text-slate-400">
          No lead with contract{" "}
          <span className="font-mono">{contract}</span> is in the live
          database, and it is not one of the demo examples. A missing lead
          is not an AVOID verdict — it only means this dashboard has no
          data for it. Check the contract on BscScan and Sourcify yourself
          before anything else.
        </p>
        <Link href="/" className="text-sm underline">
          ← Back to the lead feed
        </Link>
      </div>
    );
  }

  const ver = detail.verification;
  const score = detail.score;
  const preview = demo?.preview;

  return (
    <div className="space-y-6">
      <div>
        <Link href="/" className="text-sm text-slate-400 underline">
          ← Back to the lead feed
        </Link>
        <h1 className="mt-2 text-2xl font-bold">
          {detail.name ?? detail.contract}
        </h1>
        <p className="mt-1 font-mono text-xs text-slate-400 break-all">
          {detail.contract}
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <StatusBadge status={detail.status} />
          {isDemo && (
            <span className="rounded-full border border-sky-700 bg-sky-950 px-2.5 py-0.5 text-xs font-semibold text-sky-200">
              DEMO EXAMPLE — real mint, 2026-11-13/14
            </span>
          )}
          {score && (
            <span className="text-sm font-semibold">
              Score {score.total}/100 · {score.verdict}
              {score.hard_cap_applied && " · HARD CAP 40 APPLIED"}
            </span>
          )}
        </div>
        {detail.source_url && (
          <p className="mt-2 text-sm">
            <a
              href={detail.source_url}
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              Original post ({detail.source ?? "source"})
            </a>
          </p>
        )}
      </div>

      <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="text-lg font-semibold">On-chain verification</h2>
        {!ver ? (
          <p className="mt-2 text-sm text-slate-400">
            No verification read yet — status is UNVERIFIED, not free and
            not exhausted. A failed read is STALE, never proof of anything.
          </p>
        ) : (
          <div className="mt-2">
            <Row label="Sourcify match" value={ver.sourcify ?? "unknown"} />
            <Row
              label="Total supply"
              value={ver.total_supply === null ? "unknown" : String(ver.total_supply)}
            />
            <Row
              label="Free supply left"
              value={ver.free_left === null ? "unknown" : String(ver.free_left)}
            />
            <Row
              label="Quota per wallet left"
              value={ver.quota_left === null ? "unknown" : String(ver.quota_left)}
            />
            <Row
              label="Mint price"
              value={
                ver.mint_price === null
                  ? "unknown"
                  : ver.mint_price === "0"
                    ? "0 BNB (free, gas only)"
                    : `${ver.mint_price} BNB`
              }
            />
            <Row
              label="Paused"
              value={ver.paused === null ? "unknown" : ver.paused ? "yes" : "no"}
            />
            <Row label="Owner" value={ver.owner ?? "unknown"} />
            <Row
              label="Owner renounced?"
              value={
                ver.owner === null
                  ? "unknown"
                  : ver.owner === "0x0000000000000000000000000000000000000000"
                    ? "yes (zero address)"
                    : "no — live owner (see rubric deduction)"
              }
            />
            <p className="mt-2 text-xs text-slate-500">
              Last read: {ver.checked_at ?? "unknown"} · BSC chain 56 ·
              multi-endpoint RPC with fallback.
            </p>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="text-lg font-semibold">Rubric — 100 points</h2>
        {!score ? (
          <p className="mt-2 text-sm text-slate-400">
            Not scored yet. Missing data is never guessed — it becomes
            NEEDS HUMAN.
          </p>
        ) : (
          <div className="mt-2 space-y-3">
            {CATEGORY_LABELS.map(({ key, label, max }) => {
              const value = score.categories[key];
              return (
                <div key={key}>
                  <div className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span className="font-mono">
                      {value}/{max}
                    </span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-slate-800">
                    <div
                      className={`h-2 rounded-full ${
                        score.verdict === "AVOID" ? "bg-red-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${(value / max) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
            <p className="text-sm">
              Verdict:{" "}
              <strong
                className={
                  score.verdict === "AVOID"
                    ? "text-red-400"
                    : score.verdict === "NEEDS HUMAN"
                      ? "text-amber-400"
                      : "text-emerald-400"
                }
              >
                {score.verdict}
              </strong>
              {score.hard_cap_applied &&
                " — Hard Cap 40: Drainable Escrow. AVOID = do not mint or buy, even if free."}
            </p>
            {score.reasons.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300">
                  Deductions
                </h3>
                <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-slate-400">
                  {score.reasons.map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
            {score.missing.length > 0 && (
              <p className="text-sm text-amber-300">
                Could not be determined (not guessed):{" "}
                {score.missing.join(", ")}
              </p>
            )}
            <p className="text-xs text-slate-500">
              Scored: {score.scored_at ?? "unknown"}
              {score.note ? ` · ${score.note}` : ""}
            </p>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="text-lg font-semibold">Preview-clean check (baw, value-0)</h2>
        {!preview ? (
          <p className="mt-2 text-sm text-slate-400">
            No preview imported for this candidate yet. A preview is a
            simulation, not a mint — and it never guarantees a tokenId.
          </p>
        ) : (
          <div className="mt-2 space-y-2 text-sm">
            <p>
              Result:{" "}
              <strong className={preview.clean ? "text-emerald-400" : "text-red-400"}>
                {preview.clean ? "CLEAN" : "DIRTY — do not broadcast"}
              </strong>
            </p>
            <p className="text-slate-400">{preview.balanceChanges}</p>
            <p className="text-slate-400">{preview.risks}</p>
            <p className="font-mono text-xs text-slate-500">
              requestId {preview.requestId} · simulated {preview.simulatedAt}
            </p>
            {preview.txHash && (
              <p className="font-mono text-xs text-slate-500 break-all">
                tx {preview.txHash}
                {preview.gasUsed > 0 && ` · gas used ${preview.gasUsed.toLocaleString()}`}
              </p>
            )}
            <div className="rounded-lg border border-amber-700 bg-amber-950 px-3 py-2 text-amber-200">
              FCFS warning — the preview tokenId is only a prediction. The
              real tokenId comes from the receipt Transfer log.
              {preview.predictedTokenId && preview.actualTokenId && (
                <>
                  {" "}
                  Example: predicted #{preview.predictedTokenId}, actual #
                  {preview.actualTokenId}
                  {preview.predictedTokenId === preview.actualTokenId
                    ? " (matched this time)"
                    : " (drifted in the race — Zeroday predicted #167, actual #169)"}
                  .
                </>
              )}
            </div>
          </div>
        )}
      </section>

      <p className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-400">
        Report-only: there is no mint button on this page on purpose. If
        you decide to mint, do it from your own wallet after your own
        check — this dashboard never signs or sends anything.
      </p>
    </div>
  );
}
