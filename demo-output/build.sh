#!/usr/bin/env bash
# Mint Watchdog — demo video build pipeline (Kiroween Week 3).
# Re-runnable end to end. Produces demo-output/output.mp4 (1920x1080, <3:00).
#
# Steps:
#   1. Start the read-only API (port 8000) + Next.js dashboard (port 3000)
#      if they are not already running. Both are report-only; nothing here
#      mints, signs, or broadcasts anything.
#   2. Screenshot the real dashboard with Playwright (Chromium).
#   3. Narrate each scene (edge-tts preferred; Google Translate TTS fallback
#      when the sandbox egress proxy blocks edge-tts WebSockets).
#   4. Composite each scene (still frame + narration audio) with ffmpeg,
#      then concat all six scenes into output.mp4.
#
# Requirements: python3, ffmpeg/ffprobe, node+npm (for the dashboard).
# First run creates demo-output/.venv with edge-tts + playwright and
# installs the Chromium browser (playwright install chromium).
# No secrets, no wallet, no login anywhere in this pipeline.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo root: ~/workspace/kiroween/mint-watchdog
OUT="$PWD/demo-output"
VENV="$OUT/.venv"

echo "== 1. Python venv (edge-tts + playwright) =="
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q edge-tts playwright
# edge-tts pins its TLS trust to certifi's bundle; the sandbox egress proxy
# MITMs TLS with its own CA, so append the system CA bundle (which includes
# the egress CA) to certifi's bundle. Harmless on machines without it.
if [ -f /run/hatch/egress-tls/ca-bundle.pem ]; then
  if ! grep -q "Hatch Sandbox Egress CA" "$VENV/lib/python3.12/site-packages/certifi/cacert.pem" 2>/dev/null; then
    cat /run/hatch/egress-tls/ca-bundle.pem >> "$VENV/lib/python3.12/site-packages/certifi/cacert.pem"
  fi
fi

echo "== 2. Chromium (Playwright) =="
"$VENV/bin/playwright" install chromium --with-deps || "$VENV/bin/playwright" install chromium

echo "== 3. API + dashboard (start if not running) =="
if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  nohup python3 server/api.py --port 8000 > /tmp/mw_api.log 2>&1 &
  sleep 2
fi
if ! curl -sf http://localhost:3000/ >/dev/null 2>&1; then
  (cd app && NEXT_PUBLIC_API_URL=http://localhost:8000 nohup npm run start -- -p 3000 > /tmp/mw_next.log 2>&1 &)
  sleep 6
fi
curl -sf http://localhost:8000/health >/dev/null
curl -sf http://localhost:3000/ >/dev/null
echo "API + dashboard up."

echo "== 4. Screenshots (real dashboard footage) =="
"$VENV/bin/python" "$OUT/shoot.py"

echo "== 5. Scene 1 frame (HTML mock, no login) =="
"$VENV/bin/python" - "$OUT/scenes/scene1_problem.html" "$OUT/frames/scene1.png" <<'PYEOF'
import sys
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + html)
    pg.wait_for_timeout(500)
    pg.screenshot(path=out)
    b.close()
print("scene1 frame:", out)
PYEOF

echo "== 6. Narration =="
# edge-tts first (natural voice); fall back to Google TTS if the egress
# proxy blocks the edge-tts WebSocket handshake.
if "$VENV/bin/python" "$OUT/tts_edge.py"; then
  echo "narration: edge-tts OK"
else
  echo "narration: edge-tts failed (proxy blocks wss) — using Google TTS fallback"
  python3 "$OUT/tts_google.py"
fi

echo "== 7. Composite =="
python3 "$OUT/compose.py"
echo "DONE: $OUT/output.mp4"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height \
  -of default=noprint_wrappers=1 "$OUT/output.mp4"
