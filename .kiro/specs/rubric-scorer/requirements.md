# Rubric Scorer — requirements

**Spec:** `rubric-scorer` (component of Mint Watchdog)
**Source:** `~/AGENTS.md` — Project Evaluation Rubric (adopted 2026-11-05).
**Status:** Week 1 — implemented as code in `server/score/rubric.py`.

## The rubric (100 points)

| # | Category | Max | What it scores |
|---|----------|-----|----------------|
| 1 | Security | 30 | Source exact match, non-upgradeable; minus for live owner, pause function, identity-gating |
| 2 | Investor Protection | 25 | CRITICAL: owner-drainable funds via `withdrawFunds` (or equivalent), locked transfers, locked exit, refund at risk of failing for lack of contract balance |
| 3 | Anti-Manipulation | 20 | Per-identity allocation limits, owner-discretionary timing / grace bonus, LP formed, no on-chain wash trading |
| 4 | Transparency | 15 | Open code that honestly documents its risk gaps, non-anonymous team, independent audit |
| 5 | Market Viability | 10 | Liquidity (WBNB), paid shares sold, existing market price |

**Hard Cap 40:** a contract with Drainable Escrow is
capped at 40 regardless of other scores. Hardened 2026-11-14 by user
decision: blocked transfers are no longer required — drainable alone
is enough. (The standing rubric this scorer is based on still
requires Drainable Escrow AND Blocked Transfers; this dashboard's
scorer is deliberately stricter.)

**Verdict AVOID:** score at or below the hard cap (reference example: 38/100)
→ **JANGAN SETOR DANA — DO NOT BUY/MINT.** This applies even to a free
mint: if the owner can drain all deposited funds, there is no safe exit,
so do not mint and do not buy. Report the
project name + reason + price (if any) and move on. The auto-mint rule
never overrides an AVOID verdict.

## Requirements

- [ ] R1: `score_candidate(evidence)` returns total (0–100), the 5 category
  sub-scores, a reason for every deduction, a `missing` list, whether the
  hard cap applied, and a verdict: `PASS | AVOID | NEEDS_HUMAN`.
- [ ] R2: Hard Cap 40 is enforced exactly: Drainable Escrow →
  `total = min(total, 40)` and verdict AVOID, no exceptions.
- [ ] R3: Verdict AVOID also applies when total ≤ 40 without the hard-cap
  condition (per the reference example).
- [ ] R4: **NEVER GUESS.** Any input that cannot be determined is recorded
  in `missing` and contributes no points for the positive item it belongs
  to; the verdict is `NEEDS_HUMAN` when a critical input is missing —
  except when the hard-cap condition is positively confirmed (then AVOID
  stands even if other data is missing).
- [ ] R5: Total can never exceed 100 and never go below 0.
- [ ] R6: Every deduction carries a human-readable reason naming the
  category, the fact, and the points lost — the dashboard shows these
  verbatim, so a user can see *why* a score is what it is.
- [ ] R7: Scoring is pure and deterministic: same evidence in → same score
  out. No network, no clock, no randomness. (On-chain evidence gathering
  lives in `server/verify/`, never inside the scorer.)
- [ ] R8: Evidence is a plain dict of named booleans / numbers / None
  (see design.md for the field list). The scorer never reads the chain,
  never fetches a URL, never invents a field value.

## Acceptance criteria

- [ ] AC1: Clean evidence (all positive) scores 100 → PASS.
- [ ] AC2: Drainable Escrow (even with everything else
  perfect) scores ≤ 40 → AVOID, `hard_cap_applied == True`.
- [ ] AC3: Empty evidence `{}` → verdict NEEDS_HUMAN, `missing` non-empty.
- [ ] AC4: Removing (setting to None) any input from an AVOID verdict
  never turns it into PASS (it stays AVOID or becomes NEEDS_HUMAN).
- [ ] AC5: Total is within [0, 100] for every input combination tested.
