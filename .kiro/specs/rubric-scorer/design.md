# Rubric Scorer — design

**Spec:** `rubric-scorer` · **Implementation:** `server/score/rubric.py`
(pure function, no I/O). **Tests:** `tests/test_scorer.py`.

## Input — `evidence` dict

Every field is `True | False | None` unless noted. `None` = "could not be
determined" (RPC failed, source not found, function missing). `None` is
never treated as `False`.

```python
evidence = {
    # Security (30)
    "sourcify_exact_match": True | False | None,   # Sourcify exact match
    "upgradeable":          True | False | None,   # proxy / upgradeable
    "owner_live":           True | False | None,   # live owner address present
    "has_pause":            True | False | None,   # pause function present
    "identity_gated":       True | False | None,   # mint gated by Agent ID / identity
    # Investor Protection (25)
    "drainable_escrow":     True | False | None,   # owner can withdrawFunds / drain
    "blocked_transfers":    True | False | None,   # transfers locked
    "locked_exit":          True | False | None,   # exit / sell locked
    "refund_at_risk":       True | False | None,   # refund may fail (no contract balance)
    # Anti-Manipulation (20)
    "per_identity_limit":   True | False | None,   # per-identity allocation limit
    "owner_discretionary_timing": True | False | None,  # owner can time / grace-bonus
    "lp_formed":            True | False | None,   # liquidity pool formed
    "wash_trading":         True | False | None,   # on-chain wash trading seen
    # Transparency (15)
    "open_code_documents_risks": True | False | None,
    "team_non_anonymous":   True | False | None,
    "independent_audit":    True | False | None,
    # Market Viability (10)
    "liquidity_wbnb":       float | None,          # WBNB in pool
    "paid_shares_sold":     int | None,            # paid shares sold
    "has_market_price":     True | False | None,   # verified market price exists
}
```

Critical inputs (missing one → NEEDS_HUMAN unless hard cap confirmed):
`sourcify_exact_match`, `drainable_escrow`, `blocked_transfers`.

## Point table

| Category | Item | Points | Awarded when |
|---|---|---|---|
| Security (30) | exact match | 12 | `sourcify_exact_match is True` |
| | non-upgradeable | 8 | `upgradeable is False` |
| | no live owner | 5 | `owner_live is False` |
| | no pause function | 3 | `has_pause is False` |
| | not identity-gated | 2 | `identity_gated is False` |
| Investor Prot. (25) | not drainable | 10 | `drainable_escrow is False` |
| | transfers open | 7 | `blocked_transfers is False` |
| | exit not locked | 5 | `locked_exit is False` |
| | refund not at risk | 3 | `refund_at_risk is False` |
| Anti-Manip. (20) | per-identity limit | 7 | `per_identity_limit is True` |
| | no owner timing | 5 | `owner_discretionary_timing is False` |
| | LP formed | 5 | `lp_formed is True` |
| | no wash trading | 3 | `wash_trading is False` |
| Transparency (15) | open code documents risks | 6 | `open_code_documents_risks is True` |
| | non-anonymous team | 5 | `team_non_anonymous is True` |
| | independent audit | 4 | `independent_audit is True` |
| Market (10) | WBNB liquidity > 0 | 4 | `liquidity_wbnb is not None and > 0` |
| | paid shares sold > 0 | 3 | `paid_shares_sold is not None and > 0` |
| | market price exists | 3 | `has_market_price is True` |

Unknown (`None`) → 0 points for that item + the field name in `missing`,
except the market numbers, which are also just `missing`.

## Verdict algorithm (order matters)

```
total = sum of the 5 categories
if drainable_escrow is True:
    total = min(total, 40)
    hard_cap_applied = True
    verdict = AVOID
elif any critical input is None:
    verdict = NEEDS_HUMAN
elif total <= 40:
    verdict = AVOID
else:
    verdict = PASS
total = clamp(total, 0, 100)
```

Why this order: a positively confirmed Drainable Escrow
is decisive — it stays AVOID even if other data is missing. A missing
critical input can never silently become a PASS. A low-but-not-drainable
score (≤ 40) is still AVOID, matching the reference example (38/100).

## Output

```python
{
  "total": 78,
  "categories": {"security": 30, "investor_protection": 25,
                 "anti_manipulation": 20, "transparency": 15,
                 "market_viability": 10},
  "reasons": ["Security: source is not an exact Sourcify match (-12)", ...],
  "missing": ["independent_audit", ...],
  "hard_cap_applied": False,
  "verdict": "PASS",   # "PASS" | "AVOID" | "NEEDS_HUMAN"
}
```

## Property tests (Week 3 polish; core cases already in Week 1 tests)

- Total ∈ [0, 100] for any input combination.
- Drainable Escrow ⇒ total ≤ 40 and verdict AVOID (blocked transfers
  not required; hardened 2026-11-14).
- AVOID never becomes PASS when an input goes missing.
