"""Read-only HTTP API (stdlib http.server — no framework needed).

Endpoints:
- GET /health  -> {"status": "ok", "report_only": true}
- GET /leads   -> leads with latest score
- GET /scores  -> alias of /leads for now (dashboard convenience)
- GET /leads/<contract> -> one lead + latest verification + latest score
- GET /holdings -> recorded holdings (lock status, floor note)

Any other method -> 405. Any other path -> 404. There are deliberately
no POST/PUT/DELETE routes and no endpoint that signs, sends, or spends
anything. Report-only by design.

Usage:
    python3 server/api.py [--db PATH] [--port 8000]
"""

import argparse
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _is_address(value):
    return bool(_ADDRESS_RE.match(value or ""))

from server.store.db import get_lead_detail, init_db, list_holdings, list_leads  # noqa: E402

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "store",
    "mintwatch.db",
)


def make_handler(db_path):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, code, payload):
            body = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            # The dashboard fetches this API from the browser (feed polls
            # every 60s, holdings page on load). The API serves only public,
            # read-only data — no auth, no wallet, no writes — so any origin
            # may read it. Without this header the browser blocks those
            # reads and the feed sticks on "Loading..." (found 2026-11-14
            # while filming the demo video).
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._json(200, {"status": "ok", "report_only": True})
            elif self.path in ("/leads", "/scores"):
                conn = init_db(db_path)
                try:
                    self._json(200, {"leads": list_leads(conn)})
                finally:
                    conn.close()
            elif self.path == "/holdings":
                conn = init_db(db_path)
                try:
                    self._json(200, {"holdings": list_holdings(conn)})
                finally:
                    conn.close()
            elif self.path.startswith("/leads/0x"):
                contract = self.path[7:]
                if not _is_address(contract):
                    self._json(400, {"error": "invalid contract address"})
                    return
                conn = init_db(db_path)
                try:
                    detail = get_lead_detail(conn, contract)
                finally:
                    conn.close()
                if detail is None:
                    self._json(404, {"error": "lead not found"})
                else:
                    self._json(200, detail)
            else:
                self._json(404, {"error": "not found"})

        # No POST/PUT/DELETE/PATCH by design: anything else is 405.
        def _not_allowed(self):
            self._json(405, {"error": "method not allowed (read-only API)"})

        do_POST = _not_allowed
        do_PUT = _not_allowed
        do_DELETE = _not_allowed
        do_PATCH = _not_allowed

        def log_message(self, *args):  # keep stdout quiet
            pass

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mint Watchdog read-only API")
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite path")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.db))
    print("Mint Watchdog read-only API on http://127.0.0.1:%d" % args.port)
    print("Endpoints: GET /health, GET /leads, GET /scores,"
          " GET /leads/<contract>, GET /holdings (no writes, no wallet)")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
