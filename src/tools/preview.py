"""Build a GitHub-like preview of the profile and screenshot it.

1. Renders README.md through GitHub's own Markdown API (gfm, repo context),
   so the HTML has been through the real sanitizer.
2. Wraps it in github-markdown-css inside a profile-page layout
   (296px sidebar + 846px README column on desktop).
3. Screenshots it at several widths and both themes.

usage: GH_TOKEN=... python tools/preview.py [--shots]
"""
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "preview"
CSS = {
    "light": "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-light.css",
    "dark": "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-dark.css",
}
BG = {"light": "#ffffff", "dark": "#0d1117"}
FG = {"light": "#1f2328", "dark": "#f0f6fc"}
BORDER = {"light": "#d1d9e0", "dark": "#3d444d"}


def render_markdown():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    body = json.dumps({"text": (ROOT / "README.md").read_text(encoding="utf-8"),
                       "mode": "gfm", "context": "tahcin/tahcin"}).encode()
    req = urllib.request.Request("https://api.github.com/markdown", data=body, headers={
        "Authorization": f"bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "tahcin-preview"})
    with urllib.request.urlopen(req) as r:
        html = r.read().decode()
    # GitHub rewrites relative images to /tahcin/tahcin/raw/...; point them at the local files
    for prefix in ('src="/tahcin/tahcin/raw/main/', 'src="https://github.com/tahcin/tahcin/raw/main/',
                   'src="assets/'):
        html = html.replace(prefix, 'src="../' + ("assets/" if prefix.endswith("assets/") else ""))
    return html


def page(html, theme):
    css_file = OUT / f"github-markdown-{theme}.css"
    if not css_file.exists():
        css_file.write_bytes(urllib.request.urlopen(CSS[theme]).read())
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>tahcin, preview ({theme})</title>
<link rel="stylesheet" href="github-markdown-{theme}.css">
<style>
body{{margin:0;background:{BG[theme]};color:{FG[theme]};font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.wrap{{max-width:1280px;margin:0 auto;padding:24px 32px;display:flex;gap:24px;box-sizing:border-box}}
.side{{width:296px;flex:none}}
.side img{{width:296px;height:296px;border-radius:50%;border:1px solid {BORDER[theme]}}}
.side h1{{font-size:24px;margin:16px 0 0}} .side p{{margin:2px 0;color:#9198a1;font-size:20px;font-weight:300}}
.main{{flex:1;min-width:0}}
.box{{border:1px solid {BORDER[theme]};border-radius:6px;padding:24px}}
.label{{font-size:12px;margin-bottom:8px;color:#9198a1}}
@media (max-width:767px){{.wrap{{display:block;padding:16px}}.side{{width:auto;display:flex;gap:16px;align-items:center;margin-bottom:16px}}
.side img{{width:64px;height:64px}}.side h1{{font-size:20px;margin:0}}.side p{{font-size:16px}}.box{{padding:16px}}}}
</style></head><body><div class="wrap">
<div class="side"><img src="https://github.com/tahcin.png" alt=""><div><h1>Tahcin Sarwar</h1><p>tahcin</p></div></div>
<div class="main"><div class="label">tahcin / README.md</div>
<div class="box"><article class="markdown-body" style="background:transparent">{html}</article></div></div>
</div></body></html>"""


def shots():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for theme in ("dark", "light"):
            for w in (1280, 820, 390):
                pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1)
                pg.goto((OUT / f"{theme}.html").as_uri())
                pg.wait_for_load_state("networkidle")
                pg.wait_for_timeout(9000)  # let every sheet finish printing
                pg.screenshot(path=str(ROOT / ".snaps" / f"page_{theme}_{w}.png"), full_page=True)
                print("shot", theme, w)
                pg.close()
        b.close()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    html = render_markdown()
    for theme in ("dark", "light"):
        (OUT / f"{theme}.html").write_text(page(html, theme), encoding="utf-8")
    print("wrote", OUT)
    if "--shots" in sys.argv:
        shots()
