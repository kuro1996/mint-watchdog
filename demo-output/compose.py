"""Composite the demo video: one clip per scene, then concat.

Each scene: a 1920x1080 still frame (real dashboard screenshot or rendered
HTML scene) held for max(narration + 1.5s, minimum), with a gentle
zoompan (1.00 -> 1.06) and 0.3s fade in/out. Audio is the scene narration,
padded with silence to the clip length.

Usage: python3 demo-output/compose.py
Output: demo-output/output.mp4 (1920x1080, yuv420p, aac audio).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "scenes.json"


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def build_clip(scene: dict, idx: int) -> Path:
    frame = ROOT / scene["frame"]
    audio = ROOT / scene["audio"]
    audio_dur = probe_duration(audio)
    dur = max(audio_dur + 1.5, scene["min_duration"])
    dur = round(dur, 2)
    clip = ROOT / "audio" / f"clip{idx}.mp4"
    fps = 30
    frames = int(dur * fps)
    # Gentle Ken Burns: zoom 1.00 -> 1.06 across the clip.
    vf = (
        f"scale=1920:1080,"
        f"zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s=1920x1080:fps={fps},"
        f"fade=t=in:st=0:d=0.3,fade=t=out:st={dur - 0.3:.2f}:d=0.3,"
        f"format=yuv420p"
    )
    af = f"apad,atrim=0:{dur:.2f}"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-i", str(frame),
        "-i", str(audio),
        "-filter_complex", f"[0:v]{vf}[v];[1:a]{af}[a]",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-video_track_timescale", "30",
        str(clip),
    ], check=True)
    print(f"clip {idx} ({scene['id']}): {dur:.2f}s from {frame.name} + {audio.name}")
    return clip


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    clips = [build_clip(s, i + 1) for i, s in enumerate(manifest["scenes"])]
    concat = ROOT / "audio" / "concat.txt"
    concat.write_text("".join(f"file '{c.name}'\n" for c in clips))
    out = ROOT / "output.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", str(out),
    ], check=True)
    for c in clips:
        c.unlink(missing_ok=True)
    concat.unlink(missing_ok=True)
    print(f"wrote {out} ({probe_duration(out):.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
