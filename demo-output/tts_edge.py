"""Narration via edge-tts (preferred, natural voice).

Usage: demo-output/.venv/bin/python demo-output/tts_edge.py
Reads demo-output/narration/sceneN.txt, writes demo-output/audio/sceneN.mp3.
Voice: en-US-ChristopherNeural (neutral en-US).

Known environment quirk: the sandbox egress proxy MITMs TLS with its own
CA and does not pass the edge-tts WebSocket handshake through (101
'Invalid connection header'). The build.sh pipeline appends the egress CA
to certifi's bundle; if the wss handshake still fails, this script exits
non-zero and build.sh falls back to tts_google.py.
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
VOICE = "en-US-ChristopherNeural"


async def narrate(text: str, out: Path) -> None:
    proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    comm = edge_tts.Communicate(text, VOICE, proxy=proxy)
    await comm.save(str(out))


def main() -> int:
    for i in range(1, 7):
        text = (ROOT / "narration" / f"scene{i}.txt").read_text().strip()
        out = ROOT / "audio" / f"scene{i}.mp3"
        asyncio.run(narrate(text, out))
        if out.stat().st_size < 1000:
            print(f"scene{i}: edge-tts produced too little audio")
            return 1
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(out)],
            capture_output=True, text=True).stdout.strip()
        print(f"scene{i}: edge-tts {dur}s -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
