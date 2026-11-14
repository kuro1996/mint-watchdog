"""Mint Watchdog pipeline — one pass: ingest → verify → score → store.

Read-only by design. This script:
- reads public X + Telegram pages (no login),
- verifies each new contract on BSC via the multi-endpoint RPC client,
- scores it with the 100-point rubric (evidence built only from verified
  reads; anything unknown stays None → NEEDS HUMAN),
- stores everything in SQLite and prints a JSON summary.

It NEVER mints, claims, sells, signs, or spends. It never calls baw
(the preview is run by the user on their own machine and imported
separately). Network failures are tolerated per source: a failed source
is reported in the summary, not retried in a loop.

Usage:
    python3 server/main.py [--db PATH] [--wallet 0x...] [--no-network]

--no-network skips the live ingest/verify steps and only reports what is
already in the database (useful for a smoke run without internet).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.ingest.telegram_watch import scan_all as scan_telegram
from server.ingest.x_watch import scan_x_profile
from server.score.rubric import score_candidate
from server.store.db import (
    add_alert,
    add_score,
    add_verification,
    init_db,
    upsert_lead,
)
from server.verify.probe import verify_candidate

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "store",
    "mintwatch.db",
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _evidence_from_verification(v):
    """Build rubric evidence from verified reads only.

    Anything not read is None. Nothing is guessed. In particular:
    drainable-escrow / blocked-transfers / team / audit / LP data are
    NOT on-chain view reads, so they stay None here (NEEDS HUMAN) until
    the verifier fills them in from source review.
    """
    return {
        "sourcify_exact_match": True if v.get("sourcify") == "exact"
        else (False if v.get("sourcify") in ("match", "none") else None),
        "upgradeable": None,
        "owner_live": (
            None
            if v.get("owner") is None
            else v["owner"].lower() != "0x0000000000000000000000000000000000000000"
        ),
        "has_pause": None,
        "identity_gated": None,
        "drainable_escrow": None,
        "blocked_transfers": None,
        "locked_exit": None,
        "refund_at_risk": None,
        "per_identity_limit": None,
        "owner_discretionary_timing": None,
        "lp_formed": None,
        "wash_trading": None,
        "open_code_documents_risks": None,
        "team_non_anonymous": None,
        "independent_audit": None,
        "liquidity_wbnb": None,
        "paid_shares_sold": None,
        "has_market_price": None,
    }


def run(db_path, wallet=None, no_network=False):
    conn = init_db(db_path)
    summary = {"run_at": _now(), "sources": {}, "leads": [], "alerts": []}

    addresses = {}  # contract -> (source label, source_url)
    if not no_network:
        try:
            x = scan_x_profile()
            summary["sources"]["x"] = {
                "handle": x["handle"],
                "addresses": len(x["addresses"]),
            }
            for addr in x["addresses"]:
                addresses.setdefault(addr, ("x:@nhutqui2309", x["source_url"]))
        except Exception as exc:  # never let one source kill the run
            summary["sources"]["x"] = {"error": str(exc)}
        try:
            for report in scan_telegram():
                summary["sources"]["telegram:" + report["channel"]] = {
                    "addresses": len(report["addresses"]),
                }
                for addr in report["addresses"]:
                    addresses.setdefault(
                        addr, ("telegram:" + report["channel"], report["source_url"])
                    )
        except Exception as exc:
            summary["sources"]["telegram"] = {"error": str(exc)}

    for contract, (source, source_url) in addresses.items():
        lead_id = upsert_lead(
            conn, contract, source=source, source_url=source_url,
            first_seen=_now(), status="VERIFYING",
        )
        entry = {"contract": contract, "source": source}
        if no_network:
            entry["status"] = "SKIPPED (no-network)"
            summary["leads"].append(entry)
            continue
        verification = verify_candidate(contract, wallet=wallet)
        add_verification(conn, lead_id, verification)
        entry["verification"] = {
            "status": verification["status"],
            "sourcify": verification["sourcify"],
            "total_supply": verification["total_supply"],
            "free_left": verification["free_left"],
            "mint_price": verification["mint_price"],
        }
        if verification["status"] == "STALE":
            upsert_lead(conn, contract, status="STALE")
            entry["status"] = "STALE"
        else:
            score = score_candidate(_evidence_from_verification(verification))
            add_score(conn, lead_id, _now(), score)
            entry["score"] = {"total": score["total"], "verdict": score["verdict"]}
            free = verification["free_left"]
            price = verification["mint_price"]
            if (
                score["verdict"] == "PASS"
                and price == 0
                and free is not None
                and free > 0
            ):
                upsert_lead(conn, contract, status="VERIFIED_FREE")
                msg = (
                    "VERIFIED FREE: %s — free left %s, rubric %d/100 PASS"
                    % (contract, free, score["total"])
                )
                add_alert(conn, lead_id, _now(), "VERIFIED_FREE", msg)
                summary["alerts"].append(msg)
                entry["status"] = "VERIFIED_FREE"
            elif score["verdict"] == "AVOID":
                upsert_lead(conn, contract, status="AVOID")
                entry["status"] = "AVOID"
            else:
                upsert_lead(conn, contract, status="UNVERIFIED")
                entry["status"] = score["verdict"]
        summary["leads"].append(entry)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mint Watchdog pipeline (read-only)")
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite path")
    parser.add_argument("--wallet", default=None, help="Agent wallet address (read-only)")
    parser.add_argument("--no-network", action="store_true",
                        help="skip live ingest/verify; report DB state only")
    args = parser.parse_args(argv)
    print(json.dumps(run(args.db, wallet=args.wallet, no_network=args.no_network), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
