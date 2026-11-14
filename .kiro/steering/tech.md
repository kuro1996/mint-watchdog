# Tech steering — Mint Watchdog

## Stack (Week 1, final)

- Python 3.12, **stdlib only** + `pycryptodome` (Keccak-256 selectors only;
  the stdlib has no Keccak). See `server/requirements.txt`.
- SQLite (`server/store/mintwatch.db`, gitignored runtime data).
- Read-only HTTP API on stdlib `http.server` (`server/api.py`):
  `GET /health`, `/leads`, `/scores` only. No POST/PUT/DELETE routes.
- Frontend (Week 2): Next.js App Router + Tailwind on Vercel (free).
  Fallback: static HTML on GitHub Pages.

## Rules

1. **No wallet, no signing, no broadcast — anywhere.** No `eth_sendTransaction`,
   no `baw ... execute`, no EIP-712 signing code, no private-key handling.
   The pre-commit hook greps for these and blocks the commit.
2. **Timeouts go to `urlopen`, never to `Request`.**
   `urllib.request.Request` rejects a `timeout` kwarg; a past bug passed
   `timeout=15` to `Request` and the poller went silently blind. Every
   network call in this repo: `urllib.request.urlopen(req, timeout=5)`.
3. **RPC reads are multi-endpoint with fallback.** Order: dataseed.bnbchain.org,
   rpc.backrunshield.com, dataseed1–4.ninicoin.io, bsc-dataseed1–4.binance.org.
   5 s timeout each. All failing → STALE, never EXHAUSTED.
4. **Preview JSON rules (baw, read-only simulation — imported, never called
   by the web app):**
   - Clean fields live under `data.simulationResult`, not `data`.
   - `risks` is a dict; clean ⟺ `riskDetails` and `riskBehaviors` both empty.
   - `balanceChanges` uses key `contractAddress` (`tokenAddress` fallback).
   - ERC20 `change` may be a float (`1e+25`): compare with
     `Decimal(str(v))`, never `int(float)` equality, never `(x or -1) == 0`.
   - `baw contract-call execute` returns the hash as `data.txHash`.
   - Real tokenId only from the receipt Transfer log `topics[3]`.
5. **Calldata is built with real Keccak-256** (`Crypto.Hash.keccak`), never
   `hashlib.sha3_256` (different function, wrong selectors).
6. **The scorer is pure.** `server/score/rubric.py` does no I/O: no network,
   no clock, no randomness, same input → same output.
7. **No invented numbers.** A price, floor, or score that cannot be verified
   is rendered as "no verified floor" / NEEDS HUMAN with the missing fields.
8. **Tests must pass before any commit.** `python3 -m unittest discover -s tests -v`.
9. **Keep it simple and working over fancy.** Stdlib beats a framework;
   a passing test beats a clever abstraction.
