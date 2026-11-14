# Rubric Scorer — tasks

**Spec:** `rubric-scorer` · **Status:** Week 1 done in this build.

## Week 1 (this build)

- [x] 1. Write `.kiro/specs/rubric-scorer/` requirements, design, tasks.
- [x] 2. Implement `server/score/rubric.py` — pure `score_candidate(evidence)`
  per the design point table + verdict algorithm. No I/O, no network,
  no clock, no randomness.
- [x] 3. Implement `server/score/preview.py` — baw preview-clean check
  (`data.simulationResult`, risks dict, `contractAddress` key, Decimal
  ERC20 comparison) + receipt tokenId from Transfer log `topics[3]`.
- [x] 4. Write `tests/test_scorer.py`: clean PASS, drainable+locked →
  capped ≤ 40 AVOID, missing data → NEEDS_HUMAN, total never > 100,
  AVOID never becomes PASS when an input goes missing.
- [x] 5. Write `tests/test_preview.py`: clean preview, dirty risks,
  `contractAddress` vs `tokenAddress` key, float ERC20 `1e+25` vs `10**25`,
  receipt tokenId from `topics[3]` (preview #167 ignored, actual #169).

## Week 2 (not in this build)

- [ ] 6. Wire the scorer into the dashboard: per-category bars + reason
  list + AVOID banner; NEEDS_HUMAN shows "needs human review" with the
  missing fields listed, never a guessed score.
- [ ] 7. End-to-end scoring of 3 real examples (Lumen #1500, Zeroday #169,
  TEGONG MIAO) and compare against the human rubric scores recorded in
  the project notes; fix any divergence in the point table and document it.

## Week 3 (polish, not in this build)

- [ ] 8. Property tests: total ∈ [0, 100] for random input combinations;
  hard cap always ≤ 40; AVOID monotonic under input removal.
- [ ] 9. Document any rubric edge cases found during Week 2 in the design
  doc (e.g. identity-gating is normal for Agent ID mints — the −2 is
  kept as written in the rubric, not silently waived).
