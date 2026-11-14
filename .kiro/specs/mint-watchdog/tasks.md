# Mint Watchdog — tasks

**Spec:** `mint-watchdog` · **Timeline:** spec §7 (Week 1: 15–21 Nov 2026)
**Status:** Week 1 tasks are done in this build unless marked otherwise.
Week 2/3 items stay open and are listed here so nothing is lost.

## Week 1 — repo + backend pipeline (this build)

- [x] 1. Initialise local repo `mint-watchdog/` (git init, no remote, no push)
  with the §5 layout: `.kiro/`, `app/`, `server/`, `tests/`, `docs/`,
  `LICENSE` (MIT), `README.md`, `.gitignore` (must NOT ignore `.kiro`).
- [x] 2. Write `.kiro/specs/mint-watchdog/` requirements, design, tasks (this file).
- [x] 3. Write `.kiro/specs/rubric-scorer/` requirements, design, tasks.
- [x] 4. Write `.kiro/steering/` product, tech, structure (hard rules).
- [x] 5. Write `.kiro/hooks/` on-save test hook + pre-commit secret-scan hook.
- [x] 6. Write `.kiro/agents/` verifier + rubric-reviewer custom agents.
- [x] 7. Write `.kiro/settings/mcp.json` (github, filesystem, fetch — config
  only, no credentials).
- [x] 8. Port BSC readers from `~/workspace/bsc_read.py` (`sel`, `enc_arg`,
  multi-endpoint `eth_call`) into `server/verify/rpc.py`, with the
  5 s timeout passed to `urlopen`, never to `Request`.
- [x] 9. Implement `server/verify/sourcify.py` (exact/match/none/unknown)
  and `server/verify/probe.py` (`verify_candidate`: totalSupply,
  freeLeft/freeRemaining, quota, mint price, paused, owner; all-failed
  endpoints → status STALE, never EXHAUSTED).
- [x] 10. Implement `server/ingest/` — X @nhutqui2309 public-page reader +
  Telegram public s-page readers (agentidcall, airdropcloudJP,
  airdropfind, AIRDROPSATSETT). No login, no session tokens. Address
  extraction + dedup in `extract.py`.
- [x] 11. Implement `server/score/rubric.py` (100-point rubric as code) and
  `server/score/preview.py` (baw preview-clean check + receipt tokenId
  from Transfer log), encoding the `~/AGENTS.md` pitfalls as code + comments.
- [x] 12. Implement `server/store/db.py` (SQLite `mintwatch.db`: leads,
  verifications, scores, alerts, holdings).
- [x] 13. Implement `server/main.py` (one pipeline pass: ingest → verify →
  score → store, read-only) and `server/api.py` (stdlib read-only HTTP API:
  `GET /health`, `/leads`, `/scores`; anything else → 405).
- [x] 14. Write `tests/` (scorer, RPC fallback, preview, store, ingest) and
  make them pass on this VM: `python3 -m unittest discover -s tests -v`.
- [x] 15. Write `docs/DEMO.md` (demo script outline, spec §6) and
  `docs/KIRO-USAGE.md` (Kiro-usage write-up outline, spec §5).
- [x] 16. Write `app/README.md` placeholder (Week 2: Next.js dashboard).
- [x] 17. Write root `README.md` (what it is, how to run, security limits)
  and `LICENSE` (MIT). Grep the whole repo for secrets / private keys /
  seeds / wallet addresses beyond the one public example wallet in the
  spec — none may exist.

## Week 2 — frontend + deploy (22–28 Nov, NOT in this build)

- [ ] 18. Build `app/` (Next.js App Router + Tailwind): live lead feed,
  on-chain verification panel, rubric score breakdown, alert banner,
  holdings view, gas widget. Report-only: no mint button, no wallet connect.
- [ ] 19. Deploy frontend free on Vercel → public URL (submission requirement).
- [ ] 20. End-to-end test with 3 real examples: Lumen Findings #1500,
  Zeroday Bunker #169 (preview #167 vs actual), TEGONG MIAO +10,000,000
  (locked until sellout).
- [ ] 21. Decide frontend fallback if time is short (static HTML on GitHub
  Pages, zero build step).

## Week 3 — polish + submit (29 Nov–4 Dec, NOT in this build)

- [ ] 22. Polish + property tests for the scorer (total never > 100;
  Drainable Escrow always ≤ 40; AVOID never becomes
  PASS when an input goes missing).
- [ ] 23. Record demo video < 3 min (shot list in `docs/DEMO.md`), upload
  to YouTube (public).
- [ ] 24. Write final Devpost description + `docs/KIRO-USAGE.md` (final).
- [ ] 25. User submits on Devpost before **2026-12-04 14:00 PT**.
- [ ] 26. User requests 4,000 free Kiro credits before **2026-12-01 12:00 PT**
  (user-only step; do not do it for the user).
