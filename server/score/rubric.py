"""100-point Project Evaluation Rubric, as code (pure function).

Source: ~/AGENTS.md — Project Evaluation Rubric, adopted 2026-11-05.

Categories (max 100):
  Security 30 | Investor Protection 25 | Anti-Manipulation 20 |
  Transparency 15 | Market Viability 10.

Hard Cap 40: Drainable Escrow alone → total capped at 40,
verdict AVOID. AVOID = JANGAN SETOR DANA — do not buy/mint, even free.

Hardened 2026-11-14 by user decision ("Kerasin jadi AVOID kalau
drainable"): drainable escrow alone is enough — the owner can drain
deposited funds even when transfers are not locked. This is stricter
than the standing rubric in ~/AGENTS.md, which fires the cap only on
Drainable Escrow AND Blocked Transfers; that standing rule is unchanged
for live mint decisions. This module is the hackathon dashboard's
scorer, not the standing rule.

NEVER GUESS: an input that is None ("could not be determined") earns 0
points for its item, is listed in ``missing``, and — when it is a critical
input — makes the verdict NEEDS HUMAN instead of PASS. The only verdict
that overrides missing data is a positively confirmed hard-cap condition.

This module is pure: no I/O, no network, no clock, no randomness.
Same evidence in → same score out.
"""

SECURITY_MAX = 30
INVESTOR_PROTECTION_MAX = 25
ANTI_MANIPULATION_MAX = 20
TRANSPARENCY_MAX = 15
MARKET_VIABILITY_MAX = 10
MAX_TOTAL = 100
HARD_CAP = 40

# Inputs whose absence blocks a PASS verdict.
CRITICAL_FIELDS = ("sourcify_exact_match", "drainable_escrow", "blocked_transfers")


def score_candidate(evidence):
    """Score one candidate. ``evidence`` is a dict of named fields (see
    .kiro/specs/rubric-scorer/design.md). Returns a dict with total,
    per-category scores, reasons, missing fields, hard_cap_applied, verdict.
    """
    ev = dict(evidence or {})
    reasons = []
    missing = []

    def flag(field):
        if field not in missing:
            missing.append(field)

    # --- Security (30) ---
    security = 0
    if ev.get("sourcify_exact_match") is True:
        security += 12
    elif ev.get("sourcify_exact_match") is False:
        reasons.append("Security: source is not an exact Sourcify match (-12)")
    else:
        flag("sourcify_exact_match")
    if ev.get("upgradeable") is False:
        security += 8
    elif ev.get("upgradeable") is True:
        reasons.append("Security: upgradeable contract (-8)")
    else:
        flag("upgradeable")
    if ev.get("owner_live") is False:
        security += 5
    elif ev.get("owner_live") is True:
        reasons.append("Security: live owner (-5)")
    else:
        flag("owner_live")
    if ev.get("has_pause") is False:
        security += 3
    elif ev.get("has_pause") is True:
        reasons.append("Security: pause function present (-3)")
    else:
        flag("has_pause")
    if ev.get("identity_gated") is False:
        security += 2
    elif ev.get("identity_gated") is True:
        reasons.append("Security: identity-gated mint (-2)")
    else:
        flag("identity_gated")

    # --- Investor Protection (25) ---
    investor = 0
    if ev.get("drainable_escrow") is False:
        investor += 10
    elif ev.get("drainable_escrow") is True:
        reasons.append(
            "Investor Protection: owner can drain escrow via withdrawFunds "
            "or equivalent (-10)"
        )
    else:
        flag("drainable_escrow")
    if ev.get("blocked_transfers") is False:
        investor += 7
    elif ev.get("blocked_transfers") is True:
        reasons.append("Investor Protection: transfers are locked (-7)")
    else:
        flag("blocked_transfers")
    if ev.get("locked_exit") is False:
        investor += 5
    elif ev.get("locked_exit") is True:
        reasons.append("Investor Protection: exit / sell is locked (-5)")
    else:
        flag("locked_exit")
    if ev.get("refund_at_risk") is False:
        investor += 3
    elif ev.get("refund_at_risk") is True:
        reasons.append(
            "Investor Protection: refund at risk of failing for lack of "
            "contract balance (-3)"
        )
    else:
        flag("refund_at_risk")

    # --- Anti-Manipulation (20) ---
    anti = 0
    if ev.get("per_identity_limit") is True:
        anti += 7
    elif ev.get("per_identity_limit") is False:
        reasons.append("Anti-Manipulation: no per-identity allocation limit (-7)")
    else:
        flag("per_identity_limit")
    if ev.get("owner_discretionary_timing") is False:
        anti += 5
    elif ev.get("owner_discretionary_timing") is True:
        reasons.append(
            "Anti-Manipulation: owner-discretionary timing / grace bonus (-5)"
        )
    else:
        flag("owner_discretionary_timing")
    if ev.get("lp_formed") is True:
        anti += 5
    elif ev.get("lp_formed") is False:
        reasons.append("Anti-Manipulation: no liquidity pool formed (-5)")
    else:
        flag("lp_formed")
    if ev.get("wash_trading") is False:
        anti += 3
    elif ev.get("wash_trading") is True:
        reasons.append("Anti-Manipulation: on-chain wash trading seen (-3)")
    else:
        flag("wash_trading")

    # --- Transparency (15) ---
    transparency = 0
    if ev.get("open_code_documents_risks") is True:
        transparency += 6
    elif ev.get("open_code_documents_risks") is False:
        reasons.append(
            "Transparency: open code does not honestly document its risk "
            "gaps (-6)"
        )
    else:
        flag("open_code_documents_risks")
    if ev.get("team_non_anonymous") is True:
        transparency += 5
    elif ev.get("team_non_anonymous") is False:
        reasons.append("Transparency: anonymous team (-5)")
    else:
        flag("team_non_anonymous")
    if ev.get("independent_audit") is True:
        transparency += 4
    elif ev.get("independent_audit") is False:
        reasons.append("Transparency: no independent audit (-4)")
    else:
        flag("independent_audit")

    # --- Market Viability (10) ---
    market = 0
    liquidity = ev.get("liquidity_wbnb")
    if liquidity is None:
        flag("liquidity_wbnb")
    elif liquidity > 0:
        market += 4
    else:
        reasons.append("Market Viability: no WBNB liquidity (-4)")
    paid = ev.get("paid_shares_sold")
    if paid is None:
        flag("paid_shares_sold")
    elif paid > 0:
        market += 3
    else:
        reasons.append("Market Viability: no paid shares sold (-3)")
    if ev.get("has_market_price") is True:
        market += 3
    elif ev.get("has_market_price") is False:
        reasons.append("Market Viability: no existing market price (-3)")
    else:
        flag("has_market_price")

    total = security + investor + anti + transparency + market

    # --- Verdict (order matters) ---
    # Hardened 2026-11-14: drainable escrow ALONE triggers the cap.
    # Blocked transfers are no longer required. A drainable contract
    # scores at most 40 and is AVOID even if everything else is perfect.
    hard_cap_applied = bool(ev.get("drainable_escrow") is True)
    if hard_cap_applied:
        total = min(total, HARD_CAP)
        verdict = "AVOID"
        reasons.append(
            "Hard Cap 40 applied: Drainable Escrow — owner can drain "
            "deposited funds, total capped at 40, verdict AVOID "
            "(JANGAN SETOR DANA)"
        )
    elif any(ev.get(field) is None for field in CRITICAL_FIELDS):
        verdict = "NEEDS_HUMAN"
    elif total <= HARD_CAP:
        verdict = "AVOID"
    else:
        verdict = "PASS"

    total = max(0, min(MAX_TOTAL, total))
    return {
        "total": total,
        "categories": {
            "security": security,
            "investor_protection": investor,
            "anti_manipulation": anti,
            "transparency": transparency,
            "market_viability": market,
        },
        "reasons": reasons,
        "missing": missing,
        "hard_cap_applied": hard_cap_applied,
        "verdict": verdict,
    }
