# Mint Watchdog

**A report-only dashboard for free Binance Agent ID mints on BSC.**
Built for Kiroween 2026 (Frankenstein category).

Free-mint hunters miss 15-minute windows, burn gas on unverified mints,
and get misled by preview-predicted token IDs. Mint Watchdog pulls leads
from public X and Telegram pages, verifies each contract on-chain, scores
it with a 100-point rubric, and shows open windows, verification, and
holdings in one place — and **never mints, claims, sells, signs, or
connects a wallet**.

## What it does (Week 1)

1. **Ingest** — reads public pages of X `@nhutqui2309` and Telegram
   channels `agentidcall`, `airdropcloudJP`, `airdropfind`,
   `AIRDROPSATSETT`. No login, no session tokens, no join, no post.
2. **Verify** — multi-endpoint BSC RPC reads (with fallback and a 5 s
   timeout): Sourcify exact-match check, totalSupply, free left, quota
   per wallet, mint price, paused, owner. All endpoints failing → status
   **STALE**, never "exhausted".
3. **Score** — the 100-point rubric as pure code (Security 30, Investor
   Protection 25, Anti-Manipulation 20, Transparency 15, Market
   Viability 10). Drainable Escrow → **Hard Cap 40,
   AVOID** (hardened 2026-11-14: drainable alone is enough, blocked
   transfers no longer required). Missing data → **NEEDS HUMAN**. Nothing is guessed.
4. **Preview rules** — the baw preview pitfalls are encoded as code
   (`server/score/preview.py`): clean fields live under
   `data.simulationResult`, risks is a dict, `balanceChanges` uses
   `contractAddress`, ERC20 float changes compare via `Decimal`, the real
   tokenId comes only from the receipt Transfer log, a win counts only
   on receipt status `0x1`. The app does **not** call baw itself.
5. **Store** — SQLite (`server/store/mintwatch.db`): leads,
   verifications, scores, alerts, holdings.
6. **Read-only API** — `GET /health`, `GET /leads`, `GET /leads/<contract>`,
   `GET /holdings`, `GET /scores`. No POST/PUT/DELETE routes exist by
   design.

## What it does (Week 2 — dashboard)

Next.js App Router + Tailwind in `app/` (see `app/README.md`). It
consumes exactly the read-only API above
(`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`).

- `/` — live lead feed, newest first, source + time + link to the
  original post; status badges; an alert banner when a candidate is
  VERIFIED FREE + rubric PASS + free supply and quota left; the gas
  widget. Polls every 60 s; shows last-checked time and STALE when the
  API is unreachable.
- `/candidate/[contract]` — on-chain verification panel, rubric
  breakdown with per-deduction reasons and Hard Cap 40 flag, and the
  preview-clean display with the FCFS warning (preview tokenId is only
  a prediction; the real tokenId comes from the receipt Transfer log).
- `/holdings` — held NFTs/tokens with lock status; "no verified floor"
  wherever no price is verified.
- **Demo fixtures** — the three real mints from the spec (Lumen #1500,
  Zeroday #169, TEGONG +10,000,000 MIAO) are built in as clearly
  labelled `DEMO EXAMPLE` data, separate from live API data. The Lumen
  demo score (48 PASS) is the exact output of the rubric scorer for the
  evidence on file; the Zeroday (≈71) and TEGONG (≈65) totals are the
  approximate results recorded 2026-11-13 and are labelled as such.
- **Gas widget** — read-only BNB balance for a user-pasted address
  (public BSC RPC), last-mint gas estimate (195,342 gas, Lumen Case 6),
  low-balance warning. No transaction, no wallet connect, no signing.

## Run locally (Week 1 + Week 2)

```bash
# from the repo root
python3 -m unittest discover -s tests -t .   # 47 tests, must all pass

python3 server/main.py --no-network   # report DB state only (no network)
python3 server/main.py                # full pass: ingest -> verify -> score -> store
python3 server/api.py --port 8000     # read-only API on http://127.0.0.1:8000

# in a second terminal — the dashboard
cd app && npm install && npm run build && npm run start   # http://localhost:3000
# or: npm run dev   (development server, same port)
```

Deploy: `npx vercel --prod` from `app/` (set `NEXT_PUBLIC_API_URL` in
the Vercel project to the public URL of the read-only API; the dashboard
alone serves the UI + demo fixtures). Any plain Node host that runs
`npm run build && npm run start` works too. See `app/README.md`.

Requirements: Python 3.12, `pycryptodome` (Keccak-256 only — stdlib
hashlib has SHA3-256, which is **not** Keccak). Everything else is
stdlib; no FastAPI in Week 1 (see `server/requirements.txt`).

## Security limits — read this first

- **Report-only.** No auto-mint, no auto-sell, no wallet connect, no
  signing, no private keys or seeds anywhere in this repo.
- **No invented prices.** Where no floor/price is verified, the dashboard
  shows "no verified floor".
- **A failed read is STALE.** One failed RPC call never proves a mint is
  closed or exhausted; the app retries other endpoints and says STALE.
- **A win counts only on receipt 0x1 + token proven in the wallet.**
  The preview-predicted tokenId is never reported as the minted one
  (real examples: Zeroday predicted #167, actual #169; Lumen predicted
  #182, actual #271).

## Layout

```
.kiro/                 Kiro specs, steering, hooks, agents, MCP settings
app/                  Week 2 Next.js dashboard (feed, candidate, holdings, gas widget)
server/
  ingest/             X + Telegram public-page readers
  verify/             BSC RPC (multi-endpoint), Sourcify, on-chain probe
  score/              100-point rubric + baw preview rules
  store/              SQLite (mintwatch.db, gitignored)
  main.py             ingest -> verify -> score -> store pipeline
  api.py              read-only HTTP API (stdlib http.server)
tests/                47 unit tests (scorer, RPC fallback, preview, store, ingest, API)
docs/                 DEMO.md (demo script), KIRO-USAGE.md
```

## Status

Week 1 done (repo + `/.kiro` + port of the watchers/readers). Week 2
done: Next.js dashboard in `app/` — production build verified locally,
three pages curl-checked 200, live API reads verified. Deployed
anonymously to a temporary Vercel URL (expires ~1h, claimable by the
user — see `app/README.md`); a stable URL needs the user's own Vercel
login + claim. Week 3: demo video + Devpost submission. See
`.kiro/specs/mint-watchdog/tasks.md`.
