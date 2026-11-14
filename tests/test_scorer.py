"""Tests for the 100-point rubric scorer (server/score/rubric.py).

Spec: .kiro/specs/rubric-scorer/requirements.md (AC1–AC5).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.score.rubric import score_candidate

CLEAN = {
    "sourcify_exact_match": True,
    "upgradeable": False,
    "owner_live": False,
    "has_pause": False,
    "identity_gated": False,
    "drainable_escrow": False,
    "blocked_transfers": False,
    "locked_exit": False,
    "refund_at_risk": False,
    "per_identity_limit": True,
    "owner_discretionary_timing": False,
    "lp_formed": True,
    "wash_trading": False,
    "open_code_documents_risks": True,
    "team_non_anonymous": True,
    "independent_audit": True,
    "liquidity_wbnb": 1.5,
    "paid_shares_sold": 100,
    "has_market_price": True,
}


class TestScorer(unittest.TestCase):
    def test_clean_evidence_scores_100_pass(self):
        result = score_candidate(CLEAN)
        self.assertEqual(result["total"], 100)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["categories"]["security"], 30)
        self.assertEqual(result["categories"]["investor_protection"], 25)
        self.assertEqual(result["categories"]["anti_manipulation"], 20)
        self.assertEqual(result["categories"]["transparency"], 15)
        self.assertEqual(result["categories"]["market_viability"], 10)
        self.assertFalse(result["hard_cap_applied"])
        self.assertEqual(result["missing"], [])

    def test_drainable_plus_locked_capped_at_40_avoid(self):
        ev = dict(CLEAN, drainable_escrow=True, blocked_transfers=True,
                  locked_exit=True)
        result = score_candidate(ev)
        self.assertTrue(result["hard_cap_applied"])
        self.assertLessEqual(result["total"], 40)
        self.assertEqual(result["verdict"], "AVOID")
        self.assertTrue(any("Hard Cap 40" in r for r in result["reasons"]))

    def test_drainable_plus_locked_even_with_everything_else_perfect(self):
        # Raw score would be 78 (30+3+20+15+10); the cap must still apply.
        ev = dict(CLEAN, drainable_escrow=True, blocked_transfers=True)
        result = score_candidate(ev)
        self.assertEqual(result["total"], 40)
        self.assertEqual(result["verdict"], "AVOID")

    def test_drainable_alone_capped_at_40_avoid(self):
        # Hardened 2026-11-14 (user decision): drainable escrow alone
        # triggers the cap — blocked transfers are no longer required.
        # Old behaviour: total 90, PASS. New: total 40, AVOID.
        ev = dict(CLEAN, drainable_escrow=True, blocked_transfers=False)
        result = score_candidate(ev)
        self.assertTrue(result["hard_cap_applied"])
        self.assertEqual(result["total"], 40)
        self.assertEqual(result["verdict"], "AVOID")
        self.assertTrue(any("Hard Cap 40" in r for r in result["reasons"]))

    def test_drainable_alone_even_with_everything_else_perfect(self):
        # Raw score would be 90 (30+15+20+15+10); the cap must still apply.
        ev = dict(CLEAN, drainable_escrow=True)
        result = score_candidate(ev)
        self.assertEqual(result["total"], 40)
        self.assertEqual(result["verdict"], "AVOID")

    def test_drainable_alone_beats_missing_data(self):
        # Drainable positively confirmed -> AVOID even if other data
        # (including blocked_transfers) is missing.
        ev = {"drainable_escrow": True}
        result = score_candidate(ev)
        self.assertEqual(result["verdict"], "AVOID")
        self.assertTrue(result["hard_cap_applied"])

    def test_blocked_alone_does_not_trigger_hard_cap(self):
        # Only drainable triggers the cap. Blocked transfers alone
        # (transfers locked, exit locked) still score on the points.
        ev = dict(CLEAN, blocked_transfers=True, locked_exit=True)
        result = score_candidate(ev)
        self.assertFalse(result["hard_cap_applied"])
        self.assertEqual(result["total"], 88)
        self.assertEqual(result["verdict"], "PASS")

    def test_missing_data_needs_human(self):
        result = score_candidate({})
        self.assertEqual(result["verdict"], "NEEDS_HUMAN")
        self.assertTrue(result["missing"])
        self.assertIn("sourcify_exact_match", result["missing"])
        self.assertIn("drainable_escrow", result["missing"])
        self.assertIn("blocked_transfers", result["missing"])

    def test_missing_critical_blocks_pass_despite_high_score(self):
        # Everything positive except Sourcify unknown: never a PASS.
        ev = dict(CLEAN, sourcify_exact_match=None)
        result = score_candidate(ev)
        self.assertEqual(result["verdict"], "NEEDS_HUMAN")
        self.assertGreater(result["total"], 40)

    def test_hard_cap_beats_missing_data(self):
        # Drainable + blocked positively confirmed -> AVOID even if other
        # data is missing.
        ev = {"drainable_escrow": True, "blocked_transfers": True}
        result = score_candidate(ev)
        self.assertEqual(result["verdict"], "AVOID")
        self.assertTrue(result["hard_cap_applied"])

    def test_low_score_without_hard_cap_is_avoid(self):
        ev = dict(CLEAN)
        ev.update({
            "sourcify_exact_match": False, "upgradeable": True,
            "owner_live": True, "has_pause": True, "identity_gated": True,
            "per_identity_limit": False, "owner_discretionary_timing": True,
            "lp_formed": False, "wash_trading": True,
            "open_code_documents_risks": False, "team_non_anonymous": False,
            "independent_audit": False, "liquidity_wbnb": 0.0,
            "paid_shares_sold": 0, "has_market_price": False,
        })
        # Investor Protection stays clean (25) but everything else is 0:
        # total 25 <= 40 -> AVOID without the hard cap.
        result = score_candidate(ev)
        self.assertFalse(result["hard_cap_applied"])
        self.assertEqual(result["total"], 25)
        self.assertEqual(result["verdict"], "AVOID")

    def test_total_never_exceeds_100(self):
        cases = [CLEAN, {}, dict(CLEAN, liquidity_wbnb=999999.0,
                                 paid_shares_sold=10 ** 9)]
        for ev in cases:
            result = score_candidate(ev)
            self.assertLessEqual(result["total"], 100)
            self.assertGreaterEqual(result["total"], 0)

    def test_avoid_never_becomes_pass_when_input_goes_missing(self):
        base = dict(CLEAN, drainable_escrow=True, blocked_transfers=True,
                    locked_exit=True)
        self.assertEqual(score_candidate(base)["verdict"], "AVOID")
        for field in list(base):
            ev = dict(base)
            ev[field] = None
            verdict = score_candidate(ev)["verdict"]
            self.assertIn(verdict, ("AVOID", "NEEDS_HUMAN"),
                          msg="field %s turned AVOID into %s" % (field, verdict))


if __name__ == "__main__":
    unittest.main()
