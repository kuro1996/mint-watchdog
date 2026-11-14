"""X lead reader — public page only, NO login, NO session tokens.

Reads the public profile page of @nhutqui2309 (the standing X watch
source) and extracts contract addresses + post links from whatever the
page contains. X's public HTML is JavaScript-heavy, so this reader is
best-effort by design: it reports what it can see and says so. It never
logs in, never copies a session, never posts.

``fetcher`` is injectable so tests never hit the network: pass any
callable ``url -> str``.
"""

import urllib.request
from datetime import datetime, timezone

from .extract import extract_addresses, extract_urls

X_HANDLE = "nhutqui2309"
X_PROFILE_URL = "https://x.com/" + X_HANDLE
USER_AGENT = "MintWatchdog/1.0 (read-only; Kiroween 2026)"
TIMEOUT = 10  # seconds; passed to urlopen, never to Request


def fetch_public_page(url, timeout=TIMEOUT):
    """Fetch one public URL and return its text ("" on failure)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        # NOTE: timeout goes to urlopen, not Request.
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def scan_x_profile(fetcher=fetch_public_page):
    """Scan @nhutqui2309's public profile page for lead addresses."""
    html = fetcher(X_PROFILE_URL)
    return {
        "source": "x",
        "handle": "@" + X_HANDLE,
        "source_url": X_PROFILE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "addresses": extract_addresses(html),
        "post_urls": [u for u in extract_urls(html) if "/status/" in u],
        "note": (
            "Best-effort public-page read (X renders most content via JS); "
            "no login used. Empty addresses here means 'nothing visible', "
            "not 'no leads'."
            if not html
            else "Public-page read; no login used."
        ),
    }
