"""Telegram lead readers — public s-pages only, NO login, NO join, NO post.

Reads the public preview pages (https://t.me/s/<channel>) of the four
standing Telegram watch channels and extracts contract addresses + post
links. No session tokens, no Telegram API key, no account.

``fetcher`` is injectable so tests never hit the network: pass any
callable ``url -> str``.
"""

import re
from datetime import datetime, timezone

from .extract import extract_addresses
from .x_watch import fetch_public_page

CHANNELS = ("agentidcall", "airdropcloudJP", "airdropfind", "AIRDROPSATSETT")
POST_ID_RE = re.compile(r"t\.me/(?:s/)?([A-Za-z0-9_]+)/(\d+)")


def scan_channel(channel, fetcher=fetch_public_page):
    """Scan one channel's public s-page for lead addresses and post ids."""
    url = "https://t.me/s/%s" % channel
    html = fetcher(url)
    post_ids = []
    seen = set()
    for _chan, pid in POST_ID_RE.findall(html or ""):
        if pid not in seen:
            seen.add(pid)
            post_ids.append(pid)
    return {
        "source": "telegram",
        "channel": channel,
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "addresses": extract_addresses(html),
        "post_ids": post_ids,
        "note": "Public s-page read; no login, no join, no post.",
    }


def scan_all(fetcher=fetch_public_page):
    """Scan all four standing channels. Returns a list of channel reports."""
    return [scan_channel(channel, fetcher=fetcher) for channel in CHANNELS]
