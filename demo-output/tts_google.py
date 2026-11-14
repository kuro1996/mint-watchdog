"""Narration via Google Translate TTS (plain HTTPS GET) — fallback when the
egress proxy blocks edge-tts WebSockets (wss handshake fails through it).
Free, no key. Splits each scene file at sentence boundaries (<=190 chars
per request) and concatenates the chunks with ffmpeg.
Usage: .venv/bin/python tts_google.py   (uses system python3 + ffmpeg)
"""
import re, subprocess, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def chunks(text: str):
    # Split on sentence boundaries, keep each request short.
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out, cur = [], ""
    for p in parts:
        if len(cur) + len(p) + 1 <= 190:
            cur = (cur + " " + p).strip()
        else:
            if cur:
                out.append(cur)
            cur = p
    if cur:
        out.append(cur)
    return out

def fetch(text: str, dest: Path) -> None:
    q = urllib.parse.quote(text)
    url = (f"https://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0"
           f"&textlen={len(text)}&tl=en&client=tw-ob&q={q}")
    subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", "--max-time", "30",
                    "-o", str(dest), url], check=True)

def main() -> int:
    for i in range(1, 7):
        text = (ROOT / "narration" / f"scene{i}.txt").read_text().strip()
        parts = chunks(text)
        tmp = []
        for j, part in enumerate(parts):
            f = ROOT / "audio" / f"scene{i}_part{j}.mp3"
            fetch(part, f)
            if f.stat().st_size < 1000:
                print(f"scene{i} part{j}: suspiciously small ({f.stat().st_size}B)")
                return 1
            tmp.append(f)
        out = ROOT / "audio" / f"scene{i}.mp3"
        if len(tmp) == 1:
            tmp[0].rename(out)
        else:
            lst = ROOT / "audio" / f"scene{i}_concat.txt"
            lst.write_text("".join(f"file '{t.name}'\n" for t in tmp))
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat",
                            "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
                           check=True)
            lst.unlink()
        for t in tmp:
            t.unlink(missing_ok=True)
        dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "format=duration", "-of", "csv=p=0", str(out)],
                             capture_output=True, text=True).stdout.strip()
        print(f"scene{i}: {len(parts)} chunk(s), {dur}s -> {out.name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
