"""Address / link extraction from lead posts (pure functions).

Lead posts mention contracts as ``0x...`` addresses. This module finds
them, normalises to lowercase, and dedups them in first-seen order.
No network, no guessing: an address is only reported when it literally
appears in the source text.
"""

import re

ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")
URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def extract_addresses(text):
    """All 0x addresses in ``text``, lowercased, deduped, first-seen order."""
    seen = set()
    out = []
    for match in ADDRESS_RE.findall(text or ""):
        addr = match.lower()
        if addr not in seen:
            seen.add(addr)
            out.append(addr)
    return out


def extract_urls(text):
    """All http(s) URLs in ``text``, deduped, first-seen order."""
    seen = set()
    out = []
    for match in URL_RE.findall(text or ""):
        if match not in seen:
            seen.add(match)
            out.append(match)
    return out
