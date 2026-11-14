# Demo script — Mint Watchdog (target ≤ 2:30, hard cap 3:00)

The video shows the whole loop once, end to end, on real public data.
No wallet is connected on camera. No transaction is signed.

## Shot list (6 segments)

| # | Time | What the viewer sees | Narration (one line) |
|---|------|----------------------|----------------------|
| 1 | 0:00–0:20 | **The problem.** A lead post on X (@nhutqui2309) and a Telegram channel, side by side; a 15-minute window clock ticking. | "Free-mint hunters miss 15-minute windows and burn gas on unverified mints." |
| 2 | 0:20–0:50 | **Ingest.** The dashboard lead feed (`/`) filling with the two posts, source + time + original-post link shown; the STALE banner shown briefly with the API stopped, to prove a failed read never means "exhausted". | "Mint Watchdog reads public X and Telegram pages — no login, no session." |
| 3 | 0:50–1:20 | **Verify.** The candidate page (`/candidate/<contract>`): Sourcify exact match, totalSupply, free left, mint price, paused, owner — each read live from BSC, with the multi-endpoint fallback noted. | "Every lead is verified on-chain before anyone looks at it." |
| 4 | 1:20–1:50 | **Score.** The rubric panel on the same page: per-category bars, Hard Cap 40, and an AVOID flag on a drainable-escrow example; a NEEDS HUMAN case shown next to it. | "The 100-point rubric runs as code — drainable escrow alone is capped at 40, AVOID, even if free." |
| 5 | 1:50–2:10 | **The receipt lesson.** Lumen #1500 vs Zeroday #169 on the candidate page: the preview-predicted tokenId vs the real tokenId taken from the receipt Transfer log. | "A win counts only on receipt 0x1 plus the token proven in the wallet — never the preview's guess." |
| 6 | 2:10–2:30 | **Holdings + gas.** Holdings page (`/holdings`, "no verified floor" where no price exists) and the gas widget; closing line + repo URL. | "Report-only, free to run, useful after the hackathon too." |

Week 2 note: shots 2–6 are now recorded in the dashboard UI
(`npm run start`, http://localhost:3000) with the read-only API running
(`python3 server/api.py --port 8000`). The demo fixtures (Lumen #1500,
Zeroday #169, TEGONG) are labelled DEMO EXAMPLE on screen — say so in
the narration when they appear, so the viewer knows they are real past
mints, not live leads.

## Recording notes

- Record at 1080p, terminal font large enough to read at YouTube 720p.
- Use the real `server/main.py --no-network` output for shot 2 if the live
  network is slow; say so on screen ("cached run") — never fake a result.
- The demo must not show any private key, seed phrase, or wallet other
  than the public example in the spec (kuro1999.ai /
  0x921012ec43EC5d103E05117AdB7B0911d360F7B3).
- Publish the finished video as **public on YouTube**, under 3 minutes,
  and link it in the Devpost submission.

## Submission checklist (demo-related)

- [ ] Video < 3 min, public on YouTube
- [ ] Repo URL is public, open-source license, `/.kiro` at root
- [ ] Working app URL included (Week 2)
- [ ] Text description + Kiro-usage write-up (see `docs/KIRO-USAGE.md`)
