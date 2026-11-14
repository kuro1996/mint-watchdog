# Devpost submission draft — Mint Watchdog (Kiroween 2026, Frankenstein)

Status: DRAFT (Week 3). Demo video recorded 2026-11-14 (82s, 1920x1080,
`demo-output/output.mp4`, script `docs/DEMO.md`); YouTube upload is a
user-side step. Public GitHub repo not yet
created — the repo is local-only; publishing it is a user-side step before
submission (Devpost requires a public repo with an open-source license and
`/.kiro` at root; both are ready in this repo: MIT LICENSE, `.kiro/` present).

## Working app URL

https://mint-watchdog.vercel.app (production, Vercel, project
kuro1999/mint-watchdog, commit e8460a3)

Note for the submission: the deployed dashboard currently runs in
demo mode — it shows real past mints (Lumen #1500, Zeroday #169, TEGONG
MIAO) labelled "Demo examples — windows now closed", because the read-only
Python API (`server/api.py`) has no public host yet. The API defaults to
`http://localhost:8000`; a live feed needs `NEXT_PUBLIC_API_URL` set before
build. The dashboard is honest about this: a failed API read shows STALE,
never "exhausted".

## Title

Mint Watchdog — never miss a free mint, never burn gas on a scam

## Tagline

A report-only dashboard for free Binance Agent ID mints on BSC: it reads
public leads, verifies each contract on-chain, scores it with a 100-point
rubric, and shows open windows — and never mints, claims, sells, signs, or
connects a wallet.

## Inspiration

Free-mint hunters for Binance Agent ID projects miss 15-minute windows,
burn gas on unverified mints, and get misled by preview-predicted token
IDs. The information is scattered across X posts and Telegram channels,
and the check that matters — is this contract actually free, verified,
and safe to mint? — is manual, slow, and easy to get wrong.

## What it does

1. **Ingest** — reads public pages of X (@nhutqui2309) and Telegram
   channels (agentidcall, airdropcloudJP, airdropfind, AIRDROPSATSETT).
   No login, no session tokens, no join, no post.
2. **Verify** — multi-endpoint BSC RPC reads with fallback: Sourcify
   exact-match check, totalSupply, free left, quota per wallet, mint
   price, paused, owner. All endpoints failing → status STALE, never
   "exhausted".
3. **Score** — the 100-point rubric as pure code (Security 30, Investor
   Protection 25, Anti-Manipulation 20, Transparency 15, Market
   Viability 10). Drainable Escrow → Hard Cap 40,
   AVOID (hardened 2026-11-14: drainable alone is enough, blocked
   transfers no longer required). Missing data → NEEDS HUMAN. Nothing is guessed.
4. **Receipt lesson, encoded** — a win counts only on receipt status
   0x1 plus the token proven in the wallet; the real tokenId comes only
   from the receipt Transfer log, never from a preview (Lumen #1500 and
   Zeroday #169 both proved the preview wrong).
5. **Holdings + gas** — holdings view ("no verified floor" where no
   price exists) and a gas widget, so the hunter knows what a mint
   actually costs before spending.

## How we built it

- Week 1: spec-driven Python core (`.kiro/specs/` first, then code) —
  ingest, on-chain verification, rubric scorer, SQLite store, read-only
  stdlib API (GET only; POST/PUT/DELETE/PATCH → 405). 47/47 unit tests.
- Week 2: Next.js 15 + React 19 dashboard (`/`, `/candidate/[contract]`,
  `/holdings`) polling the API every 60 s, plus an independent
  adversarial audit and its fixes (commit e8460a3).
- Week 3: this submission, demo video (< 3 min), and the production
  deploy on the author's own Vercel account.

## Challenges we ran into

- FCFS races: a preview-predicted tokenId goes stale within seconds, so
  the dashboard only ever reports the tokenId from the receipt.
- Flaky public RPCs: every read retries across endpoints and degrades to
  STALE instead of lying.
- The rubric's hard cap: drainable escrow alone used to pass at 69
  (90 on an otherwise-clean base) — the cap only fired with blocked
  transfers too. Decided 2026-11-14: drainable alone now caps at 40,
  AVOID. This is stricter than the standing rubric the dashboard is
  based on (which requires drainable + blocked); the stricter rule is
  documented in the scorer (`server/score/rubric.py`), not hidden.

## Accomplishments we're proud of

- A dashboard that refuses to lie: STALE instead of "exhausted", NEEDS
  HUMAN instead of a guessed score, "no verified floor" instead of a
  made-up price.
- An audit that found a live Vercel token in an untracked directory and
  a misleading "live" banner — both fixed before submission.
- 47/47 tests, a clean production build, and zero wallet code anywhere
  in the repo.

## What we learned

- In a race, the plan is not the result: only receipt 0x1 + token in
  wallet counts.
- Verification is a product: the check itself is what hunters need, not
  another mint button.

## What's next

- Public host for the read-only API so the feed is live instead of demo.
- More lead sources (agentidhub, other public channels) under the same
  verify-then-report rules.
- The drainable-escrow-alone case is now decided (2026-11-14): drainable
  alone caps at 40, AVOID — see Challenges above.

## Built with

Kiro, Next.js, React, Tailwind CSS, Python (stdlib), SQLite, BSC JSON-RPC,
Sourcify, Vercel.

## Kiro usage

See `docs/KIRO-USAGE.md`: spec-driven build (`.kiro/specs/`), steering
hard rules (report-only, never guess), hooks (test on save, verify before
commit), custom agents (verifier, rubric-reviewer), MCP config. No wallet
connected, no transaction signed, no account created by Kiro. Free credits
requested via the Kiroween process; exact credit usage to be recorded in
`docs/KIRO-USAGE.md` from the Kiro console in Week 3.

## Submission checklist

- [x] Working app URL (demo mode — see note above)
- [ ] Demo video < 3 min, public on YouTube (script: `docs/DEMO.md`; recorded 2026-11-14, 82s, local file `demo-output/output.mp4` — upload is user-side)
- [ ] Public GitHub repo, MIT license, `/.kiro` at root (repo ready, not
      yet published — user-side)
- [ ] Text description (this draft)
- [ ] Kiro-usage write-up (`docs/KIRO-USAGE.md`, credits to fill in)
- [x] Open decision resolved 2026-11-14: drainable-escrow-alone hardened
      to AVOID (capped at 40)
