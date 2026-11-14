"""Tests for the BSC RPC multi-endpoint fallback (server/verify/rpc.py)
and the on-chain probe's STALE handling (server/verify/probe.py).

Rules under test (see .kiro/steering/tech.md):
- First endpoint failing falls through to the next.
- All endpoints failing raises AllEndpointsFailed; the probe turns that
  into status STALE, never EXHAUSTED.
- The 5 s timeout is passed to urlopen, never to Request.
- Selectors use real Keccak-256 (totalSupply() == 18160ddd).
"""

import io
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.error

from server.verify import probe as probe_module
from server.verify import rpc as rpc_module
from server.verify.rpc import AllEndpointsFailed, rpc_call, sel


class FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class TestRpcFallback(unittest.TestCase):
    def test_first_endpoint_failing_falls_through_to_next(self):
        calls = []

        def fake_urlopen(req, timeout=None):
            calls.append((req.full_url, timeout))
            if req.full_url == "https://first.example":
                raise urllib.error.URLError("connection refused")
            return FakeResponse({"jsonrpc": "2.0", "id": 1, "result": "0x1234"})

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result, url = rpc_call(
                "eth_blockNumber", [],
                endpoints=["https://first.example", "https://second.example"],
            )
        self.assertEqual(result, "0x1234")
        self.assertEqual(url, "https://second.example")
        self.assertEqual(len(calls), 2)

    def test_all_endpoints_failing_raises(self):
        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("down")

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(AllEndpointsFailed):
                rpc_call("eth_blockNumber", [],
                         endpoints=["https://a.example", "https://b.example"])

    def test_rpc_error_response_falls_through_to_next(self):
        def fake_urlopen(req, timeout=None):
            if "first" in req.full_url:
                return FakeResponse({"jsonrpc": "2.0", "id": 1,
                                     "error": {"code": -32000, "message": "boom"}})
            return FakeResponse({"jsonrpc": "2.0", "id": 1, "result": "0x1"})

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result, _url = rpc_call(
                "eth_blockNumber", [],
                endpoints=["https://first.example", "https://second.example"],
            )
        self.assertEqual(result, "0x1")

    def test_timeout_is_passed_to_urlopen_not_request(self):
        seen = {}

        def fake_urlopen(req, timeout=None):
            seen["timeout"] = timeout
            return FakeResponse({"jsonrpc": "2.0", "id": 1, "result": "0x1"})

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            rpc_call("eth_blockNumber", [], endpoints=["https://x.example"])
        # The 5 s timeout must reach urlopen (the past bug passed it to
        # Request, which rejects the kwarg and blinded the poller).
        self.assertEqual(seen.get("timeout"), 5)

    def test_selectors_use_real_keccak(self):
        self.assertEqual(sel("totalSupply()"), "18160ddd")
        self.assertEqual(sel("balanceOf(address)"), "70a08231")
        selector = sel("freeLeft(address)")
        self.assertEqual(len(selector), 8)
        self.assertTrue(all(c in "0123456789abcdef" for c in selector))


class TestProbeStale(unittest.TestCase):
    def test_all_endpoints_failed_means_stale_not_exhausted(self):
        def failing_eth_call(contract, data, endpoints=None, timeout=5):
            raise AllEndpointsFailed("all endpoints down")

        with mock.patch.object(probe_module, "eth_call", side_effect=failing_eth_call):
            result = probe_module.verify_candidate(
                "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591",
                sourcify_fn=lambda c: None,
            )
        self.assertEqual(result["status"], "STALE")
        self.assertNotEqual(result["status"], "EXHAUSTED")
        self.assertIsNotNone(result["error"])

    def test_successful_read_returns_values(self):
        def ok_eth_call(contract, data, endpoints=None, timeout=5):
            # Every view returns 42.
            return "0x" + "0" * 62 + "2a"

        with mock.patch.object(probe_module, "eth_call", side_effect=ok_eth_call):
            result = probe_module.verify_candidate(
                "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591",
                sourcify_fn=lambda c: "exact",
            )
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["total_supply"], 42)
        self.assertEqual(result["sourcify"], "exact")
        self.assertEqual(result["paused"], True)  # 42 != 0 -> paused flag read as True


if __name__ == "__main__":
    unittest.main()
