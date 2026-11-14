# app/ — Mint Watchdog dashboard (Week 2)

Next.js (App Router) + Tailwind v4. **Report-only**: no mint button, no
wallet connect, no signing, no private keys, no transaction anywhere in
this folder.

## Pages

- `/` — live lead feed (newest first) from the read-only API, status
  badges `NEW → VERIFYING → VERIFIED FREE / PAID / EXHAUSTED / AVOID /
  UNVERIFIED / STALE`, an alert banner when a candidate is VERIFIED FREE
  + rubric PASS + free supply and quota left, plus the gas widget.
  Polls the API every 60 s; shows last-checked time and STALE when the
  API is unreachable (a failed read never means exhausted).
- `/candidate/[contract]` — on-chain verification panel (Sourcify match,
  totalSupply, free left, quota left, mint price, paused, owner +
  renounced?), rubric breakdown (5 categories, per-deduction reasons,
  verdict PASS / AVOID / NEEDS HUMAN, Hard Cap 40 flag), and the
  preview-clean display with the FCFS warning: the preview tokenId is
  only a prediction; the real tokenId comes from the receipt Transfer log.
- `/holdings` — held NFTs/tokens with lock status. Where no price is
  verified it says **"no verified floor"** — never an invented number.

## Demo data

`src/lib/demo.ts` holds three real mints from the spec as clearly
labelled fixtures, so the dashboard is demonstrable with an empty live
feed: Lumen Findings FIND #1500 (Case 6, preview #1500 = actual #1500),
Zeroday Bunker #169 (preview #167 vs actual #169), TEGONG MIAO
+10,000,000 (locked until sellout). Demo data is separate from live API
data and marked `DEMO EXAMPLE` in the UI.

## Run locally

```bash
# Terminal 1 — the Week 1 read-only API (repo root)
python3 server/api.py --port 8000

# Terminal 2 — the dashboard (this folder)
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run start    # serve the production build
npm run lint     # ESLint (Next flat config)
```

The dashboard reads `GET /health`, `/leads`, `/leads/<contract>`,
`/holdings` from the API. Point it elsewhere with:

```bash
NEXT_PUBLIC_API_URL=https://your-api.example npm run build
```

Default: `http://localhost:8000`.

## Deploy (free)

Vercel (preferred):

```bash
npx vercel --prod
```

This needs a Vercel login — the user logs in with their own Vercel
account (created 2026-11-14); the assistant never logs in as the user.

**Expired claim — do not reuse:** the first anonymous temporary
deploy (https://agile-willow-h0pqmdg.tmp.now, 2026-11-14 ~02:36 WIB)
expired ~03:25 WIB and its claim link
(`vercel.com/claim-deployment?code=074e280a-…`) is dead — it cannot
be claimed anymore. Its token file (`app/.vercel/anonymous.json`)
was deleted 2026-11-14 during the audit (Risk #1) and must never be
committed, zipped, or uploaded. **Fresh deploy needed:** run
`npx vercel --prod` from this folder while logged in to the user's
own Vercel account; that creates a new project + stable URL.

**API URL must be set BEFORE building:** `NEXT_PUBLIC_API_URL` is a
build-time variable. Unset on Vercel it falls back to
`http://localhost:8000`, unreachable from the deployed site, so the
"live" feed shows only demo fixtures under a STALE banner — and
setting the variable after `npm run build` does nothing. Set it in
the Vercel project settings (Environment Variables) to the public
URL of the read-only API, then redeploy. The stdlib `server/api.py`
needs its own public host; the dashboard alone serves the UI and
the demo fixtures. If you have no public API host yet, the
dashboard still works — it shows STALE for live data and the demo
examples, and the feed banner never counts demo examples as open
windows (their windows are closed; see `src/app/page.tsx`).

Note: Vercel refuses to deploy vulnerable Next.js versions — keep
`next` on a patched release (15.5.29 as of 2026-11-14; `npm install
next@15.5.29 eslint-config-next@15.5.29 react@19.2.1 react-dom@19.2.1`
fixed the first deploy attempt, which 15.5.4 was rejected for).

Alternative: any static/Node host that runs `npm run build && npm run
start` (Cloudflare Pages needs the OpenNext adapter; plain Node hosting
is simpler for this app).

## Hard rules

- No `eth_sendTransaction`, no `baw … execute`, no EIP-712 signing, no
  key handling. The repo pre-commit hook greps for these.
- No invented prices or scores. Missing data → "no verified floor" /
  NEEDS HUMAN, with the missing fields listed.
- A failed read is STALE, never EXHAUSTED.
