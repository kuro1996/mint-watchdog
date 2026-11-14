"""BSC JSON-RPC client with multi-endpoint fallback (read-only).

Ported from ~/workspace/bsc_read.py (functions ``sel`` and ``call``).

Hard rules encoded here (see .kiro/steering/tech.md):
- The 5 s timeout is passed to ``urlopen``, NEVER to ``Request``.
  ``urllib.request.Request`` rejects a ``timeout`` kwarg; a past bug passed
  ``timeout=15`` to ``Request`` and the poller went silently blind.
- Calldata uses real Keccak-256 (``Crypto.Hash.keccak``), never
  ``hashlib.sha3_256`` (different function, wrong selectors).
- One endpoint failing means "try the next", never "exhausted".
  All endpoints failing raises :class:`AllEndpointsFailed`; callers turn
  that into status STALE, never EXHAUSTED.
- Read-only: only ``eth_call`` / ``eth_getTransactionReceipt`` /
  ``eth_blockNumber`` style reads. No send, no sign, no broadcast.
"""

import json
import urllib.error
import urllib.request

RPC_ENDPOINTS = [
    "https://dataseed.bnbchain.org",
    "https://rpc.backrunshield.com",
    "https://dataseed1.ninicoin.io",
    "https://dataseed2.ninicoin.io",
    "https://dataseed3.ninicoin.io",
    "https://dataseed4.ninicoin.io",
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed3.binance.org",
    "https://bsc-dataseed4.binance.org",
]

RPC_TIMEOUT = 5  # seconds; passed to urlopen, never to Request
USER_AGENT = "MintWatchdog/1.0 (read-only; Kiroween 2026)"


class AllEndpointsFailed(Exception):
    """Every RPC endpoint failed. Callers must report STALE, not EXHAUSTED."""


def sel(sig):
    """First 4 bytes of keccak256(signature), as 8 hex chars.

    Known values (sanity): sel("totalSupply()") == "18160ddd",
    sel("balanceOf(address)") == "70a08231".
    """
    try:
        from Crypto.Hash import keccak
    except ImportError as exc:  # pragma: no cover - pycryptodome is installed on the build VM
        raise RuntimeError(
            "pycryptodome is required for Keccak-256 selectors: "
            "pip install pycryptodome (see server/requirements.txt)"
        ) from exc
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return k.hexdigest()[:8]


def enc_arg(value):
    """Encode one argument (address str or int) as a 32-byte hex word."""
    if isinstance(value, str) and value.startswith("0x"):
        return value[2:].lower().rjust(64, "0")
    return format(int(value), "064x")


def calldata(sig, args=()):
    """Build 0x-prefixed calldata for a view call."""
    return "0x" + sel(sig) + "".join(enc_arg(a) for a in args)


def rpc_call(method, params, endpoints=None, timeout=RPC_TIMEOUT):
    """Call an RPC method, trying endpoints in order.

    Returns ``(result, endpoint_url)``. Raises :class:`AllEndpointsFailed`
    only after every endpoint has been tried.
    """
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    urls = list(endpoints or RPC_ENDPOINTS)
    last_error = None
    for url in urls:
        try:
            # NOTE: timeout is passed to urlopen, NOT to Request.
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            if "error" in data:
                last_error = RuntimeError(str(data["error"]))
                continue
            return data.get("result"), url
        except Exception as exc:  # network error, timeout, bad JSON, ...
            last_error = exc
            continue
    raise AllEndpointsFailed(
        "all %d RPC endpoints failed; last error: %s" % (len(urls), last_error)
    )


def eth_call(contract, data, endpoints=None, timeout=RPC_TIMEOUT):
    """Read-only eth_call. Returns the raw hex result (or "0x")."""
    result, _url = rpc_call(
        "eth_call",
        [{"to": contract, "data": data}, "latest"],
        endpoints=endpoints,
        timeout=timeout,
    )
    return result


def eth_get_transaction_receipt(tx_hash, endpoints=None, timeout=RPC_TIMEOUT):
    """Read-only receipt fetch. Returns the receipt dict or None."""
    result, _url = rpc_call(
        "eth_getTransactionReceipt", [tx_hash], endpoints=endpoints, timeout=timeout
    )
    return result
