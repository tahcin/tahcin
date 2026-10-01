"""Snapshot an SVG the way GitHub shows it: as an <img>, on a theme background.

usage: python tools/snap.py assets/hero.svg --times 0.2,1,2,4 --width 830 --theme dark
Writes PNG frames next to the scratch dir given by --out.
"""
import argparse
import os
import pathlib

from playwright.sync_api import sync_playwright

THEMES = {"light": "#ffffff", "dark": "#0d1117", "dimmed": "#212830"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("--times", default="0.5,2,5")
    ap.add_argument("--width", type=int, default=830)
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--out", default=os.environ.get("SNAP_OUT", str(pathlib.Path(__file__).resolve().parents[2] / ".snaps")))
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--reduced", action="store_true")
    a = ap.parse_args()

    svg = pathlib.Path(a.svg).resolve()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    html = (
        f"<html><body style='margin:0;padding:24px;background:{THEMES[a.theme]}'>"
        f"<img id=i src='{svg.as_uri()}' style='width:{a.width}px;display:block'></body></html>"
    )
    page_file = out / "_snap.html"
    page_file.write_text(html, encoding="utf-8")
    times = [float(t) for t in a.times.split(",")]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(
            viewport={"width": a.width + 48, "height": 400},
            device_scale_factor=a.scale,
            reduced_motion="reduce" if a.reduced else "no-preference",
        )
        pg.goto(page_file.as_uri())
        pg.wait_for_function("document.getElementById('i').complete")
        t0 = 0.0
        for t in times:
            pg.wait_for_timeout(max(0, (t - t0) * 1000))
            t0 = t
            name = f"{svg.stem}_{a.theme}_{a.width}_{t:g}s{'_rm' if a.reduced else ''}.png"
            pg.locator("body").screenshot(path=str(out / name))
            print(out / name)
        b.close()


if __name__ == "__main__":
    main()
