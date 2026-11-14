# How Kiro was used — Mint Watchdog

(For the Devpost submission's Kiro-usage write-up; expand in Week 3 with
the actual credit usage once the dashboard is built.)

## What Kiro did

- **Spec-driven build (Week 1, this repo).** The project was specified
  first in `.kiro/specs/mint-watchdog/` (requirements → design → tasks)
  and `.kiro/specs/rubric-scorer/`, then implemented against those
  specs. The spec files are the source of truth; the code follows them.
- **Steering.** `.kiro/steering/product.md`, `tech.md`, and
  `structure.md` carry the hard rules Kiro enforces on every change:
  report-only, never auto-mint/sell/sign, never guess a price or a
  score, a failed read is STALE never EXHAUSTED.
- **Hooks.** `.kiro/hooks/on-save-run-tests.json` runs the unit suite on
  save; `.kiro/hooks/before-commit-verify.json` runs the suite plus a
  secret/signature grep before any commit.
- **Custom agents.** `.kiro/agents/verifier.md` (on-chain verification
  rules) and `.kiro/agents/rubric-reviewer.md` (rubric review rules).
- **MCP.** `.kiro/settings/mcp.json` configures the github, filesystem,
  and fetch servers (config only, no credentials).

## What Kiro did NOT do

- No wallet was connected, no transaction was signed or broadcast, no
  account was created, no money was spent. The app is report-only by
  design, and Kiro never touched a private key or seed phrase (none
  exists in this repo).

## Credits

- Free credits requested via the Kiroween process (request by
  2026-12-01 12:00 PT; redeem by 2026-12-04). Exact credit usage to be
  recorded here in Week 3 from the Kiro console.
