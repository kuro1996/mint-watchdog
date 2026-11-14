"""Tests for ingest (server/ingest/*). No network: fetchers are faked."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.ingest.extract import extract_addresses, extract_urls
from server.ingest.telegram_watch import scan_all, scan_channel
from server.ingest.x_watch import scan_x_profile

CONTRACT_A = "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591"
CONTRACT_B = "0xb436617b7b5542f9c091a932654e9aeefa4a182a"


class TestExtract(unittest.TestCase):
    def test_addresses_deduped_and_lowercased(self):
        text = "mint %s and again %s plus %s" % (
            CONTRACT_A, CONTRACT_A.upper(), CONTRACT_B)
        self.assertEqual(extract_addresses(text), [CONTRACT_A, CONTRACT_B])

    def test_no_addresses(self):
        self.assertEqual(extract_addresses("no contracts here"), [])

    def test_urls_extracted(self):
        text = "see https://x.com/nhutqui2309/status/123 and https://t.me/s/agentidcall"
        self.assertEqual(extract_urls(text), [
            "https://x.com/nhutqui2309/status/123",
            "https://t.me/s/agentidcall",
        ])


class TestTelegramWatch(unittest.TestCase):
    def test_scan_channel_parses_posts_and_addresses(self):
        html = (
            '<div class="tgme_widget_message" data-post="agentidcall/123">'
            "free mint " + CONTRACT_A
            + ' <a href="https://t.me/agentidcall/123">post</a></div>'
            '<div class="tgme_widget_message" data-post="agentidcall/124">'
            "another " + CONTRACT_B
            + ' <a href="https://t.me/agentidcall/124">post</a></div>'
        )
        report = scan_channel("agentidcall", fetcher=lambda url: html)
        self.assertEqual(report["channel"], "agentidcall")
        self.assertEqual(report["addresses"], [CONTRACT_A, CONTRACT_B])
        self.assertEqual(report["post_ids"], ["123", "124"])
        self.assertIn("no login", report["note"])

    def test_scan_all_covers_four_channels(self):
        reports = scan_all(fetcher=lambda url: "")
        self.assertEqual(
            [r["channel"] for r in reports],
            ["agentidcall", "airdropcloudJP", "airdropfind", "AIRDROPSATSETT"],
        )
        for report in reports:
            self.assertEqual(report["addresses"], [])


class TestXWatch(unittest.TestCase):
    def test_scan_profile_extracts_addresses_and_status_links(self):
        html = (
            "free mint %s https://x.com/nhutqui2309/status/999" % CONTRACT_A
        )
        report = scan_x_profile(fetcher=lambda url: html)
        self.assertEqual(report["handle"], "@nhutqui2309")
        self.assertEqual(report["addresses"], [CONTRACT_A])
        self.assertEqual(report["post_urls"],
                         ["https://x.com/nhutqui2309/status/999"])

    def test_empty_page_reports_nothing_visible(self):
        report = scan_x_profile(fetcher=lambda url: "")
        self.assertEqual(report["addresses"], [])
        self.assertIn("nothing visible", report["note"])


if __name__ == "__main__":
    unittest.main()
