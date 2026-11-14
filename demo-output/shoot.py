"""Screenshot the real Mint Watchdog dashboard (localhost) for the demo video.

Usage:  demo-output/.venv/bin/python demo-output/shoot.py
Requires: local API on :8000 and Next.js on :3000 (see build.sh).
Output:   demo-output/frames/*.png  (1920x1080 each)

Dashboard shots (real footage, localhost):
  feed.png          /                       (live lead feed + demo examples box)
  candidate.png     /candidate/0x4158...   (Lumen Case 6, verification section)
  rubric.png        /candidate/0x4158...   (same page, rubric section)
  lumen_preview.png /candidate/0x4158...   (same page, preview-clean section)
  zeroday.png       /candidate/0x4789...   (Zeroday preview: predicted #167 vs actual #169)
  holdings.png      /holdings               (holdings + gas widget)

Composite scenes (HTML, rendered to PNG in the same run):
  scene1.png  scenes/scene1_problem.html  (mock X + Telegram panels, labelled mock)
  scene4.png  scenes/scene4_rubric.html   (rubric shot + Hard Cap 40 caption)
  scene5.png  scenes/scene5_receipt.html  (Lumen + Zeroday preview shots side by side)
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "frames"
LUMEN = "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
ZERODAY = "0x4789B451fAc62E5d43f916AEC3aa813C3f327312"


def shot(page, url, name, scroll_to=None, wait_ms=2500):
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(wait_ms)
    # The feed and holdings pages fetch the API from the browser; wait
    # until the client-side poll has resolved instead of filming "Loading...".
    if name in ("feed.png", "holdings.png"):
        try:
            page.wait_for_function(
                "() => !document.body.innerText.includes('Loading...')",
                timeout=10000,
            )
        except Exception:
            print(f"warn: {name} still loading after 10s, filming anyway")
        page.wait_for_timeout(500)
    if scroll_to:
        page.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (el) el.scrollIntoView({block: 'start'});
                window.scrollBy(0, -20);
            }""",
            scroll_to,
        )
        page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / name))
    print(f"shot {name} from {url}")


def render_html(page, html_path, out_name):
    page.goto("file://" + str(html_path))
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / out_name))
    print(f"rendered {out_name} from {html_path.name}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        shot(page, f"{BASE}/", "feed.png")
        shot(page, f"{BASE}/candidate/{LUMEN}", "candidate.png",
             scroll_to="section:nth-of-type(1)")
        shot(page, f"{BASE}/candidate/{LUMEN}", "rubric.png",
             scroll_to="section:nth-of-type(2)")
        shot(page, f"{BASE}/candidate/{LUMEN}", "lumen_preview.png",
             scroll_to="section:nth-of-type(3)")
        shot(page, f"{BASE}/candidate/{ZERODAY}", "zeroday.png",
             scroll_to="section:nth-of-type(3)")
        shot(page, f"{BASE}/holdings", "holdings.png")
        # Preview-clean strips for scene 5: the "Preview-clean check" panel
        # + FCFS warning box sit at y 650-930 in both candidate screenshots.
        for src, dst in (("rubric.png", "lumen_preview_strip.png"),
                         ("zeroday.png", "zeroday_preview_strip.png")):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(OUT / src),
                            "-vf", "crop=1920:280:0:650", str(OUT / dst)],
                           check=True)
            print(f"cropped {dst} from {src}")
        render_html(page, ROOT / "scenes" / "scene1_problem.html", "scene1.png")
        render_html(page, ROOT / "scenes" / "scene4_rubric.html", "scene4.png")
        render_html(page, ROOT / "scenes" / "scene5_receipt.html", "scene5.png")
        browser.close()
    print("all shots done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
