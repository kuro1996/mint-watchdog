"""Tests for the baw preview rules (server/score/preview.py).

Pitfalls under test (from ~/AGENTS.md lessons):
- Clean fields live under data.simulationResult, not data.
- risks is a dict; clean only when riskDetails AND riskBehaviors are empty.
- balanceChanges uses key contractAddress (tokenAddress fallback).
- ERC20 change can arrive as a JSON float (1e+25); compare via Decimal.
- Real tokenId comes only from the receipt Transfer log topics[3].
- execute returns the hash as data.txHash.
- A win counts only on receipt status 0x1.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.score.preview import (
    TRANSFER_TOPIC,
    balance_change_for,
    erc20_change_equals,
    execute_tx_hash,
    is_preview_clean,
    receipt_success,
    receipt_token_id,
)

CONTRACT = "0xb436617b7b5542f9c091a932654e9aeefa4a182a"  # TEGONG MIAO (example)


def clean_preview():
    return {
        "data": {
            "simulationResult": {
                "simulationErrorDetail": None,
                "balanceChanges": [
                    {"contractAddress": CONTRACT, "change": 1e25},
                ],
                "risks": {"addresses": [], "riskDetails": [], "riskBehaviors": []},
            }
        }
    }


class TestPreviewClean(unittest.TestCase):
    def test_clean_preview_is_clean(self):
        clean, reasons = is_preview_clean(clean_preview())
        self.assertTrue(clean)
        self.assertEqual(reasons, [])

    def test_nonempty_risks_dict_is_not_dirty_by_itself(self):
        # risks is a dict with populated "addresses" but empty detail lists:
        # clean, because only riskDetails / riskBehaviors count.
        preview = clean_preview()
        preview["data"]["simulationResult"]["risks"] = {
            "addresses": ["0x0000000000000000000000000000000000000001"],
            "riskDetails": [],
            "riskBehaviors": [],
        }
        clean, _ = is_preview_clean(preview)
        self.assertTrue(clean)

    def test_risk_details_make_it_dirty(self):
        preview = clean_preview()
        preview["data"]["simulationResult"]["risks"]["riskDetails"] = ["HIGH_RISK"]
        clean, reasons = is_preview_clean(preview)
        self.assertFalse(clean)
        self.assertTrue(reasons)

    def test_risk_behaviors_make_it_dirty(self):
        preview = clean_preview()
        preview["data"]["simulationResult"]["risks"]["riskBehaviors"] = ["DRAIN"]
        clean, _ = is_preview_clean(preview)
        self.assertFalse(clean)

    def test_simulation_error_makes_it_dirty(self):
        preview = clean_preview()
        preview["data"]["simulationResult"]["simulationErrorDetail"] = "revert"
        clean, _ = is_preview_clean(preview)
        self.assertFalse(clean)

    def test_empty_preview_is_not_clean(self):
        # No simulationResult at all: cannot confirm clean, never guess.
        clean, reasons = is_preview_clean({})
        self.assertFalse(clean)
        self.assertTrue(reasons)


class TestBalanceChanges(unittest.TestCase):
    def test_contract_address_key_matches(self):
        changes = [{"contractAddress": CONTRACT, "change": 10000000}]
        self.assertEqual(balance_change_for(changes, CONTRACT), 10000000)

    def test_token_address_fallback_matches(self):
        changes = [{"tokenAddress": CONTRACT, "change": 5}]
        self.assertEqual(balance_change_for(changes, CONTRACT), 5)

    def test_absent_contract_returns_none(self):
        self.assertIsNone(balance_change_for([], CONTRACT))
        self.assertIsNone(balance_change_for(
            [{"contractAddress": "0x" + "0" * 40, "change": 1}], CONTRACT))

    def test_float_erc20_change_compares_exactly(self):
        # 1e+25 as a JSON float: int(float) is NOT exactly 10**25.
        self.assertNotEqual(int(1e25), 10 ** 25)
        self.assertTrue(erc20_change_equals(1e25, 10 ** 25))
        self.assertFalse(erc20_change_equals(1e25, 10 ** 25 + 1))
        self.assertTrue(erc20_change_equals("10000000", 10_000_000))


class TestReceipt(unittest.TestCase):
    def _receipt(self, token_id):
        return {
            "status": "0x1",
            "logs": [
                {
                    "topics": [
                        TRANSFER_TOPIC,
                        "0x0000000000000000000000000000000000000000",
                        "0x921012ec43ec5d103e05117adb7b0911d360f7b3",
                        hex(token_id),
                    ]
                }
            ],
        }

    def test_token_id_comes_from_transfer_log_not_preview(self):
        # Zeroday case: preview predicted #167, receipt says #169.
        predicted = 167
        receipt = self._receipt(169)
        self.assertEqual(receipt_token_id(receipt), 169)
        self.assertNotEqual(receipt_token_id(receipt), predicted)

    def test_no_transfer_log_returns_none(self):
        self.assertIsNone(receipt_token_id({"status": "0x1", "logs": []}))

    def test_receipt_success_only_on_0x1(self):
        self.assertTrue(receipt_success({"status": "0x1"}))
        self.assertTrue(receipt_success({"status": 1}))
        self.assertFalse(receipt_success({"status": "0x0"}))
        self.assertFalse(receipt_success({}))

    def test_execute_hash_uses_tx_hash_key(self):
        self.assertEqual(
            execute_tx_hash({"data": {"txHash": "0xabc"}}), "0xabc")
        # The old wrong key must not be read.
        self.assertIsNone(
            execute_tx_hash({"data": {"transactionHash": "0xabc"}}))


if __name__ == "__main__":
    unittest.main()
