"""Sourcify source-match check (read-only, public API, no key).

Returns one of:
- ``"exact"``   — exact source match (best; the rubric's Security points
  depend on this).
- ``"match"``   — match, but not exact.
- ``"none"``    — contract is on-chain but no verified source on Sourcify.
- ``None``      — could not be determined (network error, unexpected
  response). Callers must treat this as UNKNOWN, never as "none".

Never guess: a failed check is not evidence the source is unverified.
"""

import json
import urllib.error
import urllib.request

SOURCIFY_URL = "https://sourcify.dev/server/v2/contract/56/{address}"
USER_AGENT = "MintWatchdog/1.0 (read-only; Kiroween 2026)"
TIMEOUT = 5  # seconds; passed to urlopen, never to Request


def sourcify_match(contract, timeout=TIMEOUT):
    """Check the Sourcify match status for a BSC contract address."""
    url = SOURCIFY_URL.format(address=contract)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        # NOTE: timeout goes to urlopen, not Request.
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except Exception:
        return None  # unknown, not "none"
    # Sourcify v2 returns creationMatch / runtimeMatch ("exact" | "partial" | null).
    for key in ("creationMatch", "runtimeMatch", "match"):
        value = data.get(key)
        if isinstance(value, str):
            value = value.lower()
            if value == "exact":
                return "exact"
            if value in ("partial", "match"):
                return "match"
    if data.get("message") and "not found" in str(data["message"]).lower():
        return "none"
    return None
