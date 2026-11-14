"""On-chain candidate verification (read-only).

``verify_candidate`` reads the live state of one candidate contract and
returns a plain dict the dashboard and the rubric scorer can use:

- sourcify: "exact" | "match" | "none" | None (None = unknown)
- total_supply / max_supply / free_left / quota_left / mint_price /
  paused / owner — each a value or None when it could not be read
  (function missing, call reverted, or endpoint failed for that call).
- status: "OK" | "STALE" — STALE only when every RPC endpoint failed for
  the whole verification. A single failed call never makes the whole
  candidate STALE, and nothing here ever reports EXHAUSTED.
- checked_at: ISO-8601 UTC timestamp of the read.
- endpoint: the RPC endpoint that answered the last successful call.

Never invent a value: a view that does not exist on the contract returns
None, and None is reported as "unknown", not as 0.
"""

from datetime import datetime, timezone

from .rpc import AllEndpointsFailed, calldata, eth_call
from .sourcify import sourcify_match

# Candidate view functions, tried in order. The first one that returns a
# usable value wins. Function names vary between projects, so several
# spellings are tried — the contract is never assumed to have any of them.
_TOTAL_SUPPLY_SIGS = ("totalSupply()",)
_MAX_SUPPLY_SIGS = ("maxSupply()", "MAX_SUPPLY()", "maxMint()")
_FREE_SIGS = ("freeRemaining()", "freeSupply()", "freeLeft()")
_FREE_PER_WALLET_SIGS = ("freeLeft(address)", "freeRemaining(address)")
_PAUSED_SIGS = ("paused()",)
_OWNER_SIGS = ("owner()",)
_BALANCE_SIGS = ("balanceOf(address)",)
# Mint-price view functions seen in the wild; first non-None wins.
_PRICE_SIGS = ("priceFor1()", "mintPrice()", "price()", "publicPrice()")


def _u256(raw):
    """Parse a uint256 eth_call result; None when absent/invalid."""
    if not raw or raw == "0x":
        return None
    try:
        return int(raw, 16)
    except (TypeError, ValueError):
        return None


def _try_views(contract, sigs, args=()):
    """Try each signature; return the first usable raw hex result or None."""
    for sig in sigs:
        try:
            raw = eth_call(contract, calldata(sig, args))
        except AllEndpointsFailed:
            raise
        except Exception:
            continue
        if raw and raw != "0x":
            return raw
    return None


def verify_candidate(contract, wallet=None, sourcify_fn=sourcify_match):
    """Verify one candidate contract. Read-only; never spends gas."""
    checked_at = datetime.now(timezone.utc).isoformat()
    result = {
        "contract": contract,
        "status": "OK",
        "checked_at": checked_at,
        "endpoint": None,
        "sourcify": None,
        "total_supply": None,
        "max_supply": None,
        "free_left": None,
        "quota_left": None,
        "mint_price": None,
        "paused": None,
        "owner": None,
        "error": None,
    }
    try:
        result["sourcify"] = sourcify_fn(contract)
    except Exception:
        result["sourcify"] = None

    try:
        raw = _try_views(contract, _TOTAL_SUPPLY_SIGS)
        result["total_supply"] = _u256(raw)
        raw = _try_views(contract, _MAX_SUPPLY_SIGS)
        result["max_supply"] = _u256(raw)
        raw = _try_views(contract, _FREE_SIGS)
        free_left = _u256(raw)
        if wallet:
            raw = _try_views(contract, _FREE_PER_WALLET_SIGS, args=(wallet,))
            per_wallet = _u256(raw)
            if per_wallet is not None:
                free_left = per_wallet
                result["quota_left"] = per_wallet
        result["free_left"] = free_left
        raw = _try_views(contract, _PRICE_SIGS)
        result["mint_price"] = _u256(raw)
        raw = _try_views(contract, _PAUSED_SIGS)
        paused = _u256(raw)
        result["paused"] = None if paused is None else bool(paused)
        raw = _try_views(contract, _OWNER_SIGS)
        if raw and raw != "0x":
            result["owner"] = "0x" + raw[-40:]
    except AllEndpointsFailed as exc:
        # Every RPC endpoint failed: data is stale, not exhausted.
        result["status"] = "STALE"
        result["error"] = str(exc)
    return result
