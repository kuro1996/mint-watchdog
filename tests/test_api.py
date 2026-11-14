"""Tests for the read-only API detail endpoints (Week 2).

GET /leads/<contract> and GET /holdings are read-only additions to the
Week 1 API. No POST/PUT/DELETE route may ever exist; the 405 test guards
that. Uses a real HTTP server on an ephemeral port against a temp DB.
"""

import json
import os
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from server.api import make_handler
from server.score.rubric import score_candidate
from server.store.db import (
    add_holding,
    add_score,
    add_verification,
    get_lead_id,
    init_db,
    upsert_lead,
)

CONTRACT = "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"  # Lumen Findings
OTHER = "0x4789B451fAc62E5d43f916AEC3aa813C3f327312"  # Zeroday Bunker


def _get(port, path):
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:%d%s" % (port, path), timeout=5
        ) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _request(port, path, method):
    req = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (port, path), method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


class ApiDetailTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "test.db")
        conn = init_db(self.db_path)
        upsert_lead(conn, CONTRACT, name="Lumen Findings", source="x",
                    source_url="https://x.com/example", first_seen="2026-11-13",
                    status="VERIFIED_FREE")
        lead_id = get_lead_id(conn, CONTRACT)
        add_verification(conn, lead_id, {
            "checked_at": "2026-11-13T23:46:47+07:00",
            "sourcify": "exact_match", "total_supply": 1499,
            "free_left": 1, "quota_left": 1, "mint_price": "0",
            "paused": False, "owner": "0x0000000000000000000000000000000000000000",
            "status": "VERIFIED_FREE",
        })
        score = score_candidate({
            "sourcify_exact_match": True, "upgradeable": False,
            "owner_live": False, "has_pause": False, "identity_gated": True,
            "drainable_escrow": False, "blocked_transfers": False,
            "refund_fails": False, "per_identity_cap": True,
            "owner_timing_discretion": False, "lp_formed": False,
            "wash_trading": False, "open_code": True, "team_public": False,
            "audit": False, "liquidity_wbnb": 0, "paid_shares_sold": 0,
            "market_price": None,
        })
        add_score(conn, lead_id, "2026-11-13T23:46:47+07:00", score)
        add_holding(conn, CONTRACT, token_id="1500", name="Lumen Findings #1500",
                    locked=False)
        conn.close()
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_handler(self.db_path)
        )
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def test_health(self):
        status, body = _get(self.port, "/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["report_only"])

    def test_leads_lists_score(self):
        status, body = _get(self.port, "/leads")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["leads"]), 1)
        self.assertEqual(body["leads"][0]["status"], "VERIFIED_FREE")

    def test_lead_detail_has_verification_and_score_breakdown(self):
        status, body = _get(self.port, "/leads/" + CONTRACT)
        self.assertEqual(status, 200)
        self.assertEqual(body["contract"], CONTRACT.lower())
        ver = body["verification"]
        self.assertEqual(ver["sourcify"], "exact_match")
        self.assertEqual(ver["total_supply"], 1499)
        self.assertEqual(ver["free_left"], 1)
        self.assertEqual(ver["mint_price"], "0")
        self.assertFalse(ver["paused"])
        sc = body["score"]
        self.assertIn("categories", sc)
        self.assertEqual(set(sc["categories"]),
                         {"security", "investor_protection",
                          "anti_manipulation", "transparency",
                          "market_viability"})
        self.assertIn(sc["verdict"], ("PASS", "AVOID", "NEEDS HUMAN"))
        self.assertIsInstance(sc["reasons"], list)
        self.assertIsInstance(sc["missing"], list)

    def test_lead_detail_unknown_contract_404(self):
        status, body = _get(self.port, "/leads/" + OTHER)
        self.assertEqual(status, 404)

    def test_lead_detail_invalid_address_400(self):
        status, body = _get(self.port, "/leads/0x1234")
        self.assertEqual(status, 400)

    def test_holdings(self):
        status, body = _get(self.port, "/holdings")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["holdings"]), 1)
        self.assertEqual(body["holdings"][0]["token_id"], "1500")
        self.assertEqual(body["holdings"][0]["floor_note"],
                         "no verified floor")

    def test_post_still_405(self):
        status, body = _request(self.port, "/leads", "POST")
        self.assertEqual(status, 405)


if __name__ == "__main__":
    unittest.main()
