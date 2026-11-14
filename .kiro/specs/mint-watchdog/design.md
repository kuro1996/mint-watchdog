# Mint Watchdog — design

**Spec:** `mint-watchdog` · **Source:** spec §4 (architecture) + §5 (repo layout)
**Status:** Week 1 — backend pipeline + storage + tests. Frontend (`app/`) is Week 2.

## Data flow

```
Public lead sources (no login)
  X @nhutqui2309 (poll 5 min) ─┐
  Telegram agentidcall,         ├─► Ingest: extract name + URL/contract from post,
  airdropcloudJP, airdropfind,  │    dedup by contract address, keep seen-watermark
  AIRDROPSATSETT (poll 2 min) ──┘    (JSON, same shape as the existing watch watermarks)
        │
        ▼
  Verify (on-chain, read-only)
    BSC RPC, tried in order, 5 s timeout passed to urlopen (NEVER to Request):
      1. https://dataseed.bnbchain.org
      2. https://rpc.backrunshield.com
      3. https://dataseed1.ninicoin.io (+ dataseed2–4)
      4. https://bsc-dataseed1.binance.org (+ 2–4)
    Checks: Sourcify source match → totalSupply, freeLeft/freeRemaining,
    quota per wallet, mint price, paused, owner.
    Rule: one endpoint failing means "try the next", never "exhausted".
    All endpoints failing means status STALE, never EXHAUSTED.
        │
        ▼
  Score (100-point rubric, as code — see rubric-scorer spec)
    Security 30 / Investor Protection 25 / Anti-Manipulation 20 /
    Transparency 15 / Market Viability 10. Hard Cap 40
    (Drainable Escrow) → AVOID.
    Uncomputable score → NEEDS HUMAN, never a guess.
        │
        ▼
  Preview check (baw, read-only simulation, imported — NOT called by the web app)
    `baw contract-call preview --binanceChainId 56 --value 0`
    Clean ⟺ data.simulationResult.risks.{riskDetails, riskBehaviors} both empty
    and balanceChanges (key `contractAddress`, `tokenAddress` fallback) show
    the expected change. ERC20 `change` may arrive as a JSON float (e.g. 1e+25):
    compare via Decimal(str(v)), never int(float) equality.
    Preview is run on the user's own baw-logged-in machine; its result is
    imported into the dashboard. The dashboard web app NEVER calls baw itself.
        │
        ▼
  Alert + Dashboard (Week 2 frontend)
    VERIFIED FREE + preview-clean + quota > 0 → alert.
    Dashboard: feed, verification panel, score, holdings, gas widget.
```

## Tech stack (Week 1 decision, final)

- **Backend:** Python 3.12, **stdlib only** (+ `pycryptodome` for Keccak-256
  selectors — the stdlib has no Keccak; see `server/requirements.txt`).
  FastAPI is intentionally NOT used in Week 1: it is not installed on the
  build VM, and the Week 1 deliverable is the ingest → verify → score →
  store pipeline plus a stdlib `http.server` read-only API (`server/api.py`).
  If FastAPI is wanted later, `server/api.py` is the single file to swap.
- **Storage:** SQLite, one file `server/store/mintwatch.db` (gitignored — it is
  runtime data, not source). Tables: `leads`, `verifications`, `scores`,
  `alerts`, `holdings`. No paid database. Postgres migration is not planned
  before the deadline.
- **Frontend:** Next.js (App Router) + Tailwind, deployed free on Vercel —
  Week 2. Fallback if time runs short: static HTML + vanilla JS on GitHub
  Pages (zero build step). Final call in Week 2.
- **Polling cadence:** Telegram 2 min, X 5 min, on-chain re-check of each new
  candidate + every 5 min for VERIFIED FREE candidates. Exponential backoff
  on 429. Public-RPC results cached 30–60 s.

## Data schema (SQLite)

```sql
leads(id INTEGER PRIMARY KEY, contract TEXT UNIQUE, name TEXT,
      source TEXT, source_url TEXT, first_seen TEXT, status TEXT)
  -- status: NEW | VERIFYING | VERIFIED_FREE | PAID | EXHAUSTED | AVOID
  --         | UNVERIFIED | STALE
verifications(id INTEGER PRIMARY KEY, lead_id INTEGER, checked_at TEXT,
      sourcify TEXT, total_supply INTEGER, free_left INTEGER,
      quota_left INTEGER, mint_price TEXT, paused INTEGER, owner TEXT,
      status TEXT)
scores(id INTEGER PRIMARY KEY, lead_id INTEGER, scored_at TEXT,
      total INTEGER, security INTEGER, investor_protection INTEGER,
      anti_manipulation INTEGER, transparency INTEGER, market_viability INTEGER,
      verdict TEXT, hard_cap INTEGER, reasons TEXT, missing TEXT)
  -- verdict: PASS | AVOID | NEEDS_HUMAN
alerts(id INTEGER PRIMARY KEY, lead_id INTEGER, created_at TEXT,
      kind TEXT, message TEXT, seen INTEGER)
holdings(id INTEGER PRIMARY KEY, contract TEXT, token_id TEXT, name TEXT,
      locked INTEGER, floor_note TEXT)
  -- floor_note is either a verified price string or exactly "no verified floor"
```

## Internal API (read-only, stdlib `http.server`, `server/api.py`)

- `GET /health` → `{"status": "ok", "report_only": true}`
- `GET /leads` → leads with latest verification + score
- `GET /scores` → scored candidates
- Any other method → 405. There are deliberately no POST/PUT/DELETE routes
  and no endpoint that signs, sends, or spends anything.

## Lessons encoded (from real incidents — do not re-learn them)

- `curl` beats `urllib` for flaky RPCs; in Python, `timeout` goes to
  `urlopen`, NEVER to `Request` (a past bug passed `timeout=15` to `Request`,
  which rejects it, and the poller went blind).
- Preview JSON lives under `data.simulationResult`, not `data`; `risks` is a
  dict — clean only when `riskDetails` and `riskBehaviors` are both empty;
  a non-empty dict is NOT dirty by itself.
- `balanceChanges` uses key `contractAddress`, not `tokenAddress`.
- ERC20 `change` can arrive as a float (`1e+25`); compare via
  `Decimal(str(v))`.
- The real tokenId comes only from the receipt Transfer log `topics[3]`;
  a preview tokenId is a prediction (Zeroday: predicted #167, actual #169).
- A win counts only on receipt status `0x1` + token proven in wallet.
- Scripts and state live in the workspace, never `/tmp` (VM replacement
  wipes `/tmp`).
- Never state a planned outcome as certain; check pool cap, free supply,
  quota, and window end first.
