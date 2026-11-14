"""Tests for SQLite storage (server/store/db.py)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.score.rubric import score_candidate
from server.store.db import (
    add_alert,
    add_holding,
    add_score,
    add_verification,
    get_lead_id,
    init_db,
    list_leads,
    upsert_lead,
)

CONTRACT = "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591"  # Shanhai Beasts (example)


class TestStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "test.db")
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_upsert_lead_dedups_by_contract(self):
        first = upsert_lead(self.conn, CONTRACT, name="Shanhai", source="x",
                            first_seen="2026-11-14T00:00:00+00:00")
        second = upsert_lead(self.conn, CONTRACT.upper(), name="Shanhai",
                             source="x", first_seen="2026-11-14T01:00:00+00:00")
        self.assertEqual(get_lead_id(self.conn, CONTRACT), first)
        self.assertEqual(len(list_leads(self.conn)), 1)

    def test_default_db_path_is_inside_server_store(self):
        # Regression: main.py/api.py once pointed at <repo>/store/ (which
        # does not exist) instead of <repo>/server/store/ and crashed on
        # first run with "unable to open database file".
        from server import api as api_module
        from server import main as main_module

        for path in (main_module.DEFAULT_DB, api_module.DEFAULT_DB):
            parent = os.path.dirname(path)
            self.assertEqual(os.path.basename(parent), "store")
            self.assertEqual(os.path.basename(os.path.dirname(parent)), "server")
            self.assertTrue(os.path.isdir(parent))

    def test_verification_score_alert_holding_roundtrip(self):
        lead_id = upsert_lead(self.conn, CONTRACT, name="Shanhai", source="x",
                              first_seen="2026-11-14T00:00:00+00:00")
        add_verification(self.conn, lead_id, {
            "checked_at": "2026-11-14T00:00:00+00:00", "sourcify": "exact",
            "total_supply": 4212, "free_left": 100, "quota_left": 2,
            "mint_price": 0, "paused": False,
            "owner": "0x0000000000000000000000000000000000000000",
            "status": "OK",
        })
        score = score_candidate({
            "sourcify_exact_match": True, "upgradeable": False,
            "owner_live": False, "has_pause": False, "identity_gated": False,
            "drainable_escrow": False, "blocked_transfers": False,
            "locked_exit": False, "refund_at_risk": False,
            "per_identity_limit": True, "owner_discretionary_timing": False,
            "lp_formed": True, "wash_trading": False,
            "open_code_documents_risks": True, "team_non_anonymous": True,
            "independent_audit": True, "liquidity_wbnb": 1.0,
            "paid_shares_sold": 10, "has_market_price": True,
        })
        self.assertEqual(score["total"], 100)
        add_score(self.conn, lead_id, "2026-11-14T00:00:00+00:00", score)
        add_alert(self.conn, lead_id, "2026-11-14T00:00:00+00:00",
                  "VERIFIED_FREE", "VERIFIED FREE: test")
        add_holding(self.conn, CONTRACT, token_id="4211", name="Shanhai #4211",
                    locked=1, floor_note="no verified floor")

        leads = list_leads(self.conn)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["contract"], CONTRACT)
        self.assertEqual(leads[0]["score_total"], 100)
        self.assertEqual(leads[0]["score_verdict"], "PASS")
        rows = self.conn.execute(
            "SELECT floor_note FROM holdings WHERE contract = ?", (CONTRACT,)
        ).fetchall()
        self.assertEqual(rows[0][0], "no verified floor")


if __name__ == "__main__":
    unittest.main()
